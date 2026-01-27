#!/usr/bin/env python3
"""
Bitcoin Blockchain Analyzer for R-value Reuse Detection

This script analyzes Bitcoin blockchain transactions for ECDSA signature
R-value reuse, which can lead to private key recovery. This is related to
seed security and demonstrates why proper random number generation is critical.

This tool can be used alongside the Electrum seed generator to understand
cryptographic vulnerabilities in Bitcoin transactions.
"""

import json
import socket
import hashlib
from typing import Dict, List, Optional, Tuple
import sys


class ElectrumServerConnection:
    """Connection handler for Electrum server protocol."""
    
    def __init__(self, host: str = 'electrum.blockstream.info', port: int = 50001):
        """
        Initialize connection to Electrum server.
        
        Args:
            host: Electrum server hostname
            port: Electrum server port
        """
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 0
        
    def connect(self) -> bool:
        """
        Establish connection to Electrum server.
        
        Returns:
            True if connection successful
        """
        try:
            self.socket = socket.create_connection((self.host, self.port), timeout=30)
            print(f"[INFO] Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Close connection to server."""
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def send_request(self, method: str, params: List) -> Optional[Dict]:
        """
        Send JSON-RPC request to Electrum server.
        
        Args:
            method: RPC method name
            params: Method parameters
            
        Returns:
            Response dictionary or None on error
        """
        if not self.socket:
            print("[ERROR] Not connected to server")
            return None
        
        self.request_id += 1
        request = {
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        request_str = json.dumps(request) + '\n'
        print(f"[DEBUG] Sending request: {json.dumps(request)}")
        
        try:
            self.socket.sendall(request_str.encode('utf-8'))
            response_data = self.socket.recv(4096).decode('utf-8')
            
            if not response_data:
                print("[ERROR] Empty response from server")
                return None
            
            print(f"[DEBUG] Server response: {response_data.strip()}")
            response = json.loads(response_data)
            
            if 'error' in response:
                print(f"[ERROR] Server error: {response['error']}")
                return None
            
            return response.get('result')
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse response: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return None
    
    def get_block_height(self) -> Optional[int]:
        """
        Get current blockchain height.
        
        Returns:
            Block height or None on error
        """
        result = self.send_request("blockchain.headers.subscribe", [])
        if result and 'height' in result:
            height = result['height']
            print(f"[DEBUG] Latest block height: {height}")
            return height
        return None
    
    def get_block_header(self, height: int) -> Optional[str]:
        """
        Get block header for a specific height.
        
        Args:
            height: Block height
            
        Returns:
            Block header hex string or None on error
        """
        result = self.send_request("blockchain.block.header", [height])
        if result:
            print(f"[DEBUG] Fetched block header for height {height}")
        return result


class BitcoinBlockAnalyzer:
    """Analyzer for Bitcoin blockchain data."""
    
    def __init__(self, connection: ElectrumServerConnection):
        """
        Initialize analyzer.
        
        Args:
            connection: Connected Electrum server connection
        """
        self.connection = connection
        self.r_values = {}  # Track R-values across transactions
        
    def analyze_blocks(self, start_height: int = 0, end_height: Optional[int] = None, max_blocks: int = 100):
        """
        Analyze blocks for R-value reuse.
        
        Args:
            start_height: Starting block height
            end_height: Ending block height (None for current)
            max_blocks: Maximum number of blocks to analyze
        """
        if end_height is None:
            end_height = self.connection.get_block_height()
            if end_height is None:
                print("[ERROR] Failed to get blockchain height")
                return
        
        # Limit the scan to avoid excessive server load
        actual_end = min(start_height + max_blocks, end_height)
        
        print(f"[INFO] Starting scan from block {start_height} to {actual_end}")
        print(f"[INFO] Note: Full transaction analysis requires additional RPC methods")
        print(f"[INFO] This demonstration shows block header retrieval")
        
        # Skip genesis block
        if start_height == 0:
            print("[INFO] Skipping the Genesis block.")
            start_height = 1
        
        blocks_analyzed = 0
        for height in range(start_height, actual_end + 1):
            if blocks_analyzed >= max_blocks:
                print(f"[INFO] Reached maximum block limit ({max_blocks})")
                break
            
            print(f"\n[INFO] Fetching block header for height: {height}")
            header = self.connection.get_block_header(height)
            
            if header:
                print(f"[INFO] Block {height} header: {header[:80]}...")
                blocks_analyzed += 1
            else:
                print(f"[WARNING] Failed to fetch block {height}")
                continue
            
            # Note: Full transaction analysis would require additional methods:
            # - blockchain.transaction.get_batch (for transactions in block)
            # - Parsing transaction data for signature R-values
            # This is beyond the scope of basic Electrum server protocol
        
        print(f"\n[INFO] Analysis complete. Processed {blocks_analyzed} blocks.")
        print("[NOTE] Full R-value reuse detection requires parsing raw transaction data.")
        print("[NOTE] For complete analysis, consider using Bitcoin Core RPC or specialized tools.")


def main():
    """Main entry point for the analyzer."""
    print("[DEBUG] Script has started.")
    print("[INFO] Bitcoin R-Value Reuse Analyzer")
    print("[INFO] This tool demonstrates blockchain analysis for cryptographic weaknesses\n")
    
    # Parse command line arguments
    start_block = 2  # Skip genesis and first block
    max_blocks = 10  # Limit for demonstration
    
    if len(sys.argv) > 1:
        try:
            start_block = int(sys.argv[1])
        except ValueError:
            print(f"[ERROR] Invalid start block: {sys.argv[1]}")
            return
    
    if len(sys.argv) > 2:
        try:
            max_blocks = int(sys.argv[2])
        except ValueError:
            print(f"[ERROR] Invalid max blocks: {sys.argv[2]}")
            return
    
    # Connect to Electrum server
    connection = ElectrumServerConnection()
    
    if not connection.connect():
        print("[ERROR] Failed to establish server connection")
        return
    
    try:
        # Create analyzer and run
        analyzer = BitcoinBlockAnalyzer(connection)
        analyzer.analyze_blocks(start_height=start_block, max_blocks=max_blocks)
        
    except KeyboardInterrupt:
        print("\n[INFO] Analysis interrupted by user")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connection.disconnect()
        print("\n[INFO] Connection closed")


if __name__ == '__main__':
    main()
