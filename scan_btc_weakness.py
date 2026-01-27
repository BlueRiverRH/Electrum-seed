#!/usr/bin/env python3
"""
Bitcoin Transaction Weakness Scanner - R-Value Reuse Detection

This script scans Bitcoin blockchain transactions for ECDSA signature weaknesses,
specifically R-value reuse which can lead to private key recovery.

Scans recent transactions first, then goes back in time as bandwidth allows.
"""

import os
import json
import socket
import time
import hashlib
from collections import defaultdict
from typing import Optional, List, Dict, Tuple

# Electrum server configuration
ELECTRUM_SERVER = ('blockstream.info', 110)  # SSL port
ELECTRUM_SERVER_ALT = ('electrum.blockstream.info', 50001)  # Non-SSL fallback
OUTPUT_FOUND = 'found_weaknesses_daily.txt'
CHECKPOINT_FILE = 'last_processed_block.txt'

SCAN_DELAY = 1  # Delay in seconds between blocks to avoid overloading the server
BATCH_SIZE = 100   # Number of transactions to process per block
MAX_BLOCKS_PER_RUN = 50  # Maximum blocks to scan in one run

# Track R-values globally
r_value_database = defaultdict(list)  # r_value -> [(txid, input_index)]

# ===== Debug Startup =====
print("[DEBUG] Script has started.")


# ====== Electrum Node Connection ======
def electrum_request(method: str, params: list, server_addr=None) -> Optional[dict]:
    """Make Electrum server JSON-RPC requests."""
    if server_addr is None:
        server_addr = ELECTRUM_SERVER_ALT  # Use non-SSL by default
    
    try:
        with socket.create_connection(server_addr, timeout=15) as s:
            s.settimeout(15)
            request = json.dumps({"id": 1, "method": method, "params": params}) + "\n"
            print(f"[DEBUG] Sending request: {request.strip()}")
            s.sendall(request.encode())
            
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b"\n" in response:
                    break
            
            print(f"[DEBUG] Server response: {response.decode().strip()}")
            result = json.loads(response.decode())
            
            if "error" in result:
                print(f"[ERROR] Server returned error: {result['error']}")
                return None
            
            return result.get("result", None)
    except socket.timeout:
        print(f"[ERROR] Electrum request timed out for method: {method}, params: {params}")
        return None
    except Exception as e:
        print(f"[ERROR] Electrum request failed: {e}")
        return None


def get_latest_block_height() -> Optional[int]:
    """Get the current blockchain height."""
    result = electrum_request("blockchain.headers.subscribe", [])
    if isinstance(result, dict) and "height" in result:
        height = result["height"]
        print(f"[DEBUG] Latest block height: {height}")
        return height
    print("[ERROR] Could not retrieve block height.")
    return None


def get_block_header(height: int) -> Optional[str]:
    """Get the block header at a given height."""
    print(f"[DEBUG] Fetching block header for height: {height}")
    result = electrum_request("blockchain.block.header", [height])
    return result


def parse_block_header(header_hex: str) -> Optional[Dict]:
    """Parse block header to extract block hash and other info."""
    if not header_hex or len(header_hex) < 160:
        return None
    
    try:
        # Block header is 80 bytes (160 hex chars)
        header_bytes = bytes.fromhex(header_hex[:160])
        # Double SHA256 to get block hash
        block_hash = hashlib.sha256(hashlib.sha256(header_bytes).digest()).digest()
        # Reverse for display (Bitcoin convention)
        block_hash_hex = block_hash[::-1].hex()
        
        return {
            'hash': block_hash_hex,
            'header': header_hex[:160]
        }
    except Exception as e:
        print(f"[ERROR] Failed to parse block header: {e}")
        return None


def get_block_txids(height: int) -> Optional[List[str]]:
    """Get transaction IDs in a block at given height."""
    print(f"[DEBUG] Fetching transactions for block height: {height}")
    
    # Get block header first
    header = get_block_header(height)
    if not header:
        return None
    
    block_info = parse_block_header(header)
    if not block_info:
        return None
    
    block_hash = block_info['hash']
    print(f"[INFO] Block {height} hash: {block_hash}")
    
    # Note: Electrum protocol doesn't have a direct method to get all txids from a block
    # We would need to use blockchain.transaction.id_from_pos for each position
    # For now, we'll return the block hash and note this limitation
    
    # Try to get transaction count (not directly supported, would need workaround)
    print(f"[INFO] Block header retrieved. Transaction enumeration requires additional methods.")
    
    return [block_hash]  # Placeholder - real implementation needs tx enumeration


def get_transaction(txid: str) -> Optional[str]:
    """Fetch raw transaction hex from Electrum."""
    print(f"[DEBUG] Fetching raw transaction for TXID: {txid}")
    result = electrum_request("blockchain.transaction.get", [txid, False])
    return result


def get_transaction_verbose(txid: str) -> Optional[dict]:
    """Fetch transaction with verbose output."""
    print(f"[DEBUG] Fetching verbose transaction for TXID: {txid}")
    result = electrum_request("blockchain.transaction.get", [txid, True])
    return result


# ====== Signature Analysis ======
def extract_r_from_der_signature(sig_hex: str) -> Optional[str]:
    """
    Extract R value from DER-encoded ECDSA signature.
    
    DER signature format:
    0x30 [total-length] 0x02 [R-length] [R] 0x02 [S-length] [S]
    """
    try:
        sig_bytes = bytes.fromhex(sig_hex)
        
        if len(sig_bytes) < 8:
            return None
        
        # Check for DER signature marker
        if sig_bytes[0] != 0x30:
            return None
        
        # Get R value
        r_start = 4
        r_len = sig_bytes[3]
        
        if len(sig_bytes) < r_start + r_len:
            return None
        
        r_value = sig_bytes[r_start:r_start + r_len]
        
        # Return hex representation
        return r_value.hex()
    except Exception as e:
        print(f"[WARN] Failed to parse DER signature: {sig_hex[:40]}... ({e})")
        return None


def parse_scriptsig(scriptsig_hex: str) -> List[str]:
    """
    Parse scriptSig to extract signatures.
    
    Typical scriptSig for P2PKH:
    [sig-length] [signature+sighash] [pubkey-length] [pubkey]
    """
    signatures = []
    
    try:
        script_bytes = bytes.fromhex(scriptsig_hex)
        pos = 0
        
        while pos < len(script_bytes):
            if pos >= len(script_bytes):
                break
            
            # Get data length
            length = script_bytes[pos]
            pos += 1
            
            if length == 0 or length > 75:  # Not a data push
                break
            
            if pos + length > len(script_bytes):
                break
            
            data = script_bytes[pos:pos + length]
            pos += length
            
            # Check if this looks like a signature (starts with 0x30)
            if data[0] == 0x30:
                # Remove sighash byte (last byte)
                sig_data = data[:-1] if len(data) > 1 else data
                signatures.append(sig_data.hex())
        
    except Exception as e:
        print(f"[WARN] Failed to parse scriptSig: {scriptsig_hex[:40]}... ({e})")
    
    return signatures


def analyze_transaction_simple(tx_hex: str, txid: str) -> Dict[str, List[Tuple[str, int]]]:
    """
    Analyze a transaction for R-value reuse (simplified version without bitcoinlib).
    
    Returns:
        Dictionary mapping R-values to list of (txid, input_index) tuples
    """
    r_values_found = {}
    
    try:
        # Parse raw transaction (simplified - full parsing is complex)
        tx_bytes = bytes.fromhex(tx_hex)
        
        # Skip version (4 bytes)
        pos = 4
        
        # Read input count (varint)
        if pos >= len(tx_bytes):
            return r_values_found
        
        input_count = tx_bytes[pos]
        pos += 1
        
        if input_count >= 0xfd:
            print(f"[WARN] Complex varint for inputs, skipping transaction {txid}")
            return r_values_found
        
        print(f"[DEBUG] Transaction {txid} has {input_count} inputs")
        
        # Parse each input
        for input_idx in range(input_count):
            if pos + 36 > len(tx_bytes):
                break
            
            # Skip previous output (32 bytes hash + 4 bytes index)
            pos += 36
            
            # Get scriptSig length
            if pos >= len(tx_bytes):
                break
            
            script_len = tx_bytes[pos]
            pos += 1
            
            if script_len >= 0xfd:
                # Complex varint, skip this transaction
                print(f"[WARN] Complex varint for scriptSig length in {txid}")
                return r_values_found
            
            if pos + script_len > len(tx_bytes):
                break
            
            # Extract scriptSig
            scriptsig_hex = tx_bytes[pos:pos + script_len].hex()
            pos += script_len
            
            # Skip sequence (4 bytes)
            pos += 4
            
            # Parse signatures from scriptSig
            signatures = parse_scriptsig(scriptsig_hex)
            
            for sig_hex in signatures:
                r_value = extract_r_from_der_signature(sig_hex)
                if r_value:
                    print(f"[DEBUG] Found R-value: {r_value} in tx {txid} input {input_idx}")
                    if r_value not in r_values_found:
                        r_values_found[r_value] = []
                    r_values_found[r_value].append((txid, input_idx))
        
    except Exception as e:
        print(f"[ERROR] Failed to analyze transaction {txid}: {e}")
    
    return r_values_found


def check_r_value_reuse(r_values: Dict[str, List[Tuple[str, int]]]):
    """
    Check if any R-values have been reused and report findings.
    """
    reused_r_values = []
    
    for r_value, locations in r_values.items():
        # Check against global database
        if r_value in r_value_database:
            # R-value reuse detected!
            previous_uses = r_value_database[r_value]
            all_uses = previous_uses + locations
            
            print(f"\n[ALERT] R-VALUE REUSE DETECTED!")
            print(f"[ALERT] R-value: {r_value}")
            print(f"[ALERT] Used in {len(all_uses)} different signatures:")
            for txid, input_idx in all_uses:
                print(f"[ALERT]   - Transaction: {txid}, Input: {input_idx}")
            
            reused_r_values.append({
                'r_value': r_value,
                'uses': all_uses
            })
            
            # Save to output file
            save_weakness(r_value, all_uses)
        
        # Add to global database
        r_value_database[r_value].extend(locations)
    
    return reused_r_values


def save_weakness(r_value: str, locations: List[Tuple[str, int]]):
    """Save detected weakness to output file."""
    with open(OUTPUT_FOUND, 'a') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"R-VALUE REUSE DETECTED!\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"R-value: {r_value}\n")
        f.write(f"Used in {len(locations)} signatures:\n")
        for txid, input_idx in locations:
            f.write(f"  - Transaction: {txid}, Input: {input_idx}\n")
        f.write(f"{'='*80}\n")
    
    print(f"[INFO] Weakness saved to {OUTPUT_FOUND}")


# ====== Checkpoint Management ======
def load_checkpoint() -> int:
    """Load the last processed block height."""
    if not os.path.exists(CHECKPOINT_FILE):
        print("[INFO] No checkpoint found, starting from latest block")
        return -1
    
    try:
        with open(CHECKPOINT_FILE, "r") as f:
            height = int(f.read().strip())
            print(f"[INFO] Loaded checkpoint: block {height}")
            return height
    except Exception as e:
        print(f"[ERROR] Failed to load checkpoint: {e}")
        return -1


def save_checkpoint(height: int):
    """Save the last processed block height."""
    try:
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(str(height))
        print(f"[DEBUG] Checkpoint saved: block {height}")
    except Exception as e:
        print(f"[ERROR] Failed to save checkpoint: {e}")


# ====== Main Scanner ======
def scan_blockchain():
    """
    Scan the blockchain for transaction weaknesses.
    Starts from recent blocks and works backwards.
    """
    latest_block = get_latest_block_height()
    
    if latest_block is None:
        print("[ERROR] Could not fetch the latest block height.")
        return
    
    # Get checkpoint
    last_processed = load_checkpoint()
    
    # If no checkpoint, start from latest
    if last_processed < 0:
        start_block = latest_block
    else:
        # Continue from where we left off, going backwards
        start_block = last_processed - 1
    
    # Ensure we don't go below block 2 (skip genesis and block 1)
    if start_block < 2:
        print("[INFO] Reached block 2, starting over from latest")
        start_block = latest_block
    
    end_block = max(2, start_block - MAX_BLOCKS_PER_RUN)
    
    print(f"[INFO] Starting scan from block {start_block} down to {end_block}")
    print(f"[INFO] Latest blockchain height: {latest_block}")
    
    blocks_scanned = 0
    
    for height in range(start_block, end_block - 1, -1):
        if height == 0 or height == 1:
            print(f"[INFO] Skipping block {height}")
            continue
        
        print(f"\n[INFO] Scanning block {height}")
        
        # Get block header
        header = get_block_header(height)
        if not header:
            print(f"[ERROR] Could not fetch block header for height {height}")
            continue
        
        block_info = parse_block_header(header)
        if not block_info:
            print(f"[ERROR] Could not parse block header for height {height}")
            continue
        
        print(f"[INFO] Block {height} hash: {block_info['hash']}")
        
        # Note: Full transaction scanning requires additional Electrum methods
        # or a Bitcoin node with full RPC access
        # This is a limitation of the Electrum protocol
        
        print(f"[INFO] Block {height} header retrieved successfully")
        print(f"[NOTE] Full transaction analysis requires blockchain.transaction.id_from_pos method")
        print(f"[NOTE] Or direct Bitcoin node RPC access for complete scanning")
        
        blocks_scanned += 1
        
        # Save checkpoint
        save_checkpoint(height)
        
        # Small delay to avoid overwhelming the server
        if SCAN_DELAY > 0:
            time.sleep(SCAN_DELAY)
    
    print(f"\n[INFO] Scan complete. Processed {blocks_scanned} blocks.")
    print(f"[INFO] R-values tracked: {len(r_value_database)}")
    
    if r_value_database:
        print(f"[INFO] Results saved to: {OUTPUT_FOUND}")


def main():
    """Main entry point."""
    print("[INFO] Bitcoin Transaction Weakness Scanner")
    print("[INFO] Scanning for R-value reuse in ECDSA signatures\n")
    
    try:
        scan_blockchain()
    except KeyboardInterrupt:
        print("\n[INFO] Scan interrupted by user")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
