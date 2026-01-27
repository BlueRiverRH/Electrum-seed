#!/usr/bin/env python3
"""
Test/Demo for Bitcoin Transaction Weakness Scanner

This script demonstrates the R-value reuse detection without requiring
a live connection to an Electrum server.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scan_btc_weakness import (
    extract_r_from_der_signature,
    parse_scriptsig,
    analyze_transaction_simple,
    check_r_value_reuse,
    r_value_database,
    save_weakness
)


def test_r_extraction():
    """Test R-value extraction from DER signatures."""
    print("[TEST] Testing R-value extraction from DER signatures")
    print("=" * 80)
    
    # Example DER signature (from Bitcoin testnet)
    # Format: 0x30 [length] 0x02 [r-length] [r-value] 0x02 [s-length] [s-value]
    test_signatures = [
        # Valid DER signature
        "3045022100abcdef1234567890abcdef1234567890abcdef1234567890abcdef123456789002201234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        # Another valid signature with same R (reuse!)
        "3045022100abcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678900220fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
        # Different R value
        "30450221009876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba02201234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    ]
    
    r_values = []
    for i, sig in enumerate(test_signatures):
        r_val = extract_r_from_der_signature(sig)
        r_values.append(r_val)
        print(f"[TEST] Signature {i+1}: R = {r_val}")
    
    # Check for reuse
    if r_values[0] == r_values[1]:
        print(f"\n[DEMO] ✓ R-VALUE REUSE DETECTED!")
        print(f"[DEMO] Signatures 1 and 2 use the same R-value: {r_values[0]}")
        print(f"[DEMO] This is a critical vulnerability!")
    
    print()


def test_scriptsig_parsing():
    """Test scriptSig parsing."""
    print("[TEST] Testing scriptSig parsing")
    print("=" * 80)
    
    # Example P2PKH scriptSig:
    # [sig_length] [signature+sighash] [pubkey_length] [pubkey]
    
    # Simplified test scriptSig (signature length + signature + pubkey length + pubkey)
    test_scriptsig = (
        "48"  # 72 bytes signature length
        "3045022100abcdef1234567890abcdef1234567890abcdef1234567890abcdef123456789002201234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef01"  # sig + sighash
        "21"  # 33 bytes pubkey length
        "02" + "ab" * 32  # compressed pubkey
    )
    
    print(f"[TEST] Test scriptSig: {test_scriptsig[:80]}...")
    signatures = parse_scriptsig(test_scriptsig)
    print(f"[TEST] Extracted {len(signatures)} signature(s)")
    
    for i, sig in enumerate(signatures):
        print(f"[TEST] Signature {i+1}: {sig[:60]}...")
        r_val = extract_r_from_der_signature(sig)
        print(f"[TEST] R-value: {r_val}")
    
    print()


def test_reuse_detection():
    """Test R-value reuse detection across multiple transactions."""
    print("[TEST] Testing R-value reuse detection")
    print("=" * 80)
    
    # Simulate finding same R-value in different transactions
    r_value = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    
    # First transaction
    tx1_r_values = {r_value: [("tx_abc123", 0)]}
    print(f"[TEST] Transaction 1 uses R-value: {r_value[:40]}...")
    
    # Add to database
    for r, locs in tx1_r_values.items():
        r_value_database[r].extend(locs)
    
    # Second transaction with same R-value (reuse!)
    tx2_r_values = {r_value: [("tx_def456", 0)]}
    print(f"[TEST] Transaction 2 uses R-value: {r_value[:40]}...")
    
    # Check for reuse
    reused = check_r_value_reuse(tx2_r_values)
    
    if reused:
        print(f"\n[DEMO] ✓ Successfully detected R-value reuse!")
        print(f"[DEMO] Found {len(reused)} reused R-value(s)")
    else:
        print(f"[DEMO] No reuse detected (unexpected)")
    
    print()


def test_full_workflow():
    """Test the complete workflow with mock data."""
    print("[TEST] Testing complete workflow")
    print("=" * 80)
    
    print("""
[DEMO] Simulating blockchain scan:

1. Connect to Electrum server ✓ (mocked)
2. Get latest block height ✓ (mocked: 934019)
3. Fetch block headers ✓
4. Extract transactions ✓
5. Parse signatures ✓
6. Extract R-values ✓
7. Check for reuse ✓
8. Save findings ✓

[DEMO] In a real scan:
- The scanner connects to an Electrum server
- Downloads block headers for recent blocks
- Fetches transaction data
- Parses ECDSA signatures from inputs
- Extracts R-values from each signature
- Compares R-values across all transactions
- Detects when the same R-value is reused
- Reports findings and saves to file

[DEMO] Why R-value reuse is critical:
When the same R-value is used in two different ECDSA signatures with
the same private key, the private key can be calculated using:

  k = (z1 - z2) / (s1 - s2)  mod n
  private_key = (s*k - z) / r  mod n

Where:
- k is the reused nonce (R = k*G)
- z1, z2 are message hashes
- s1, s2 are signature S values
- r is the reused R value
- n is the curve order

This is why proper random number generation is CRITICAL in Bitcoin!
""")
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("Bitcoin Transaction Weakness Scanner - Test Suite")
    print("=" * 80 + "\n")
    
    test_r_extraction()
    test_scriptsig_parsing()
    test_reuse_detection()
    test_full_workflow()
    
    print("=" * 80)
    print("[TEST] All tests completed!")
    print("=" * 80)
    print()
    print("[INFO] To run the actual scanner:")
    print("       python3 scan_btc_weakness.py")
    print()
    print("[NOTE] The scanner requires connection to an Electrum server")
    print("[NOTE] Edit ELECTRUM_SERVER in scan_btc_weakness.py to configure")
    print()


if __name__ == '__main__':
    main()
