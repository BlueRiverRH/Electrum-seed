# Bitcoin Transaction Weakness Scanner

## Overview

This scanner analyzes Bitcoin blockchain transactions for ECDSA signature weaknesses, specifically R-value reuse. When the same R-value (nonce) is used in two different ECDSA signatures with the same private key, the private key can be mathematically recovered.

## Why This Matters

R-value reuse is a **critical security vulnerability** in ECDSA signatures:

1. **Private Key Recovery**: When an attacker finds two signatures using the same R-value from the same private key, they can calculate the private key using:
   ```
   k = (z1 - z2) / (s1 - s2) mod n
   private_key = (s*k - z) / r mod n
   ```

2. **Historical Cases**: 
   - Sony PlayStation 3 signing key breach (2010) - Fixed R-value
   - Android Bitcoin wallet theft (2013) - Weak RNG
   - Multiple blockchain compromises due to poor random number generation

3. **Prevention**: This tool helps identify such weaknesses in the wild.

## Installation

No external dependencies required - uses only Python standard library.

```bash
cd Electrum-seed
python3 scan_btc_weakness.py
```

## Usage

### Basic Scanning

Run the scanner to analyze recent Bitcoin transactions:

```bash
python3 scan_btc_weakness.py
```

The scanner will:
1. Connect to an Electrum server
2. Get the latest blockchain height
3. Start scanning from recent blocks backward
4. Extract signatures from transaction inputs
5. Identify R-value reuse across transactions
6. Save findings to `found_weaknesses_daily.txt`
7. Maintain checkpoint in `last_processed_block.txt`

### Configuration

Edit `scan_btc_weakness.py` to configure:

```python
# Electrum server
ELECTRUM_SERVER_ALT = ('electrum.blockstream.info', 50001)

# Output file
OUTPUT_FOUND = 'found_weaknesses_daily.txt'

# Checkpoint file
CHECKPOINT_FILE = 'last_processed_block.txt'

# Scanning parameters
SCAN_DELAY = 1  # Seconds between blocks
MAX_BLOCKS_PER_RUN = 50  # Blocks per scan session
```

### Testing

Run the test suite to see the scanner in action (no server required):

```bash
python3 test_weakness_scanner.py
```

Output:
```
[DEMO] ✓ R-VALUE REUSE DETECTED!
[DEMO] Signatures 1 and 2 use the same R-value
[DEMO] This is a critical vulnerability!
```

## How It Works

### 1. Block Fetching

```
[INFO] Starting scan from block 934019 down to 933969
[INFO] Scanning block 934019
[DEBUG] Fetching block header for height: 934019
```

### 2. Transaction Analysis

For each block:
1. Fetch block header
2. Extract block hash
3. Enumerate transactions (via Electrum protocol)
4. Parse transaction inputs

### 3. Signature Parsing

For each transaction input:
```python
# Extract scriptSig
scriptsig = get_scriptsig_from_input(input)

# Parse signatures
signatures = parse_scriptsig(scriptsig)

# Extract R-values
for sig in signatures:
    r_value = extract_r_from_der_signature(sig)
    track_r_value(r_value, txid, input_index)
```

### 4. Reuse Detection

```python
# Check if R-value seen before
if r_value in r_value_database:
    # WEAKNESS FOUND!
    report_weakness(r_value, current_tx, previous_txs)
```

### 5. Output

When R-value reuse is detected:

```
================================================================================
R-VALUE REUSE DETECTED!
Timestamp: 2026-01-27 22:46:22
R-value: 00abcdef1234567890...
Used in 2 signatures:
  - Transaction: tx_abc123..., Input: 0
  - Transaction: tx_def456..., Input: 1
================================================================================
```

## DER Signature Format

ECDSA signatures in Bitcoin use DER encoding:

```
0x30 [total-length]
  0x02 [r-length] [r-value]
  0x02 [s-length] [s-value]
[sighash-byte]
```

Example:
```
30450221 00abcdef... 0220 1234567... 01
^        ^           ^    ^          ^
|        |           |    |          sighash
|        |           |    S value
|        |           S marker
|        R value     
R marker
```

## Checkpoint System

The scanner maintains progress in `last_processed_block.txt`:

```python
# Load checkpoint
last_block = load_checkpoint()  # e.g., 933950

# Scan from last_block backward
for height in range(last_block - 1, last_block - 50, -1):
    scan_block(height)
    save_checkpoint(height)
```

This allows:
- Resuming after interruption
- Scanning in batches
- Tracking progress
- Avoiding duplicate work

## Scanning Strategy

### Daily Transaction Focus

1. **Start Recent**: Begin with latest blocks (most recent transactions)
2. **Work Backward**: Process older blocks as bandwidth allows
3. **Checkpoint Progress**: Save state after each block
4. **Resume Capability**: Continue from last processed block

### Bandwidth Management

```python
# Scan recent blocks first
if no_checkpoint:
    start = latest_block
else:
    start = checkpoint - 1

# Process in batches
end = start - MAX_BLOCKS_PER_RUN

# Small delay between requests
time.sleep(SCAN_DELAY)
```

## Limitations

### Electrum Protocol

The Electrum server protocol has some limitations:

1. **No Direct Transaction List**: Can't directly get all transactions in a block
2. **Transaction Enumeration**: Need to use `blockchain.transaction.id_from_pos`
3. **Rate Limiting**: Servers may throttle excessive requests

### Workarounds

For complete scanning, consider:
- Using Bitcoin Core RPC directly
- Running a local Bitcoin node
- Using block explorer APIs
- Implementing batch transaction fetching

## Performance

### Expected Throughput

- **Blocks per second**: ~0.5-1 (with SCAN_DELAY=1)
- **Blocks per hour**: ~1800-3600
- **Days of history per hour**: ~1.25-2.5 days

### Optimization Tips

1. **Reduce SCAN_DELAY**: Faster scanning (but higher server load)
2. **Increase MAX_BLOCKS_PER_RUN**: Process more per session
3. **Run continuously**: Use cron/systemd for background scanning
4. **Local Bitcoin node**: Eliminate network latency

## Security Considerations

### What to Do When Weakness Found

If you discover R-value reuse:

1. **Document**: Save all transaction IDs and R-values
2. **Analyze**: Determine if private key compromise is possible
3. **Report**: Consider responsible disclosure if affecting live wallets
4. **Research**: Investigate root cause (RNG failure, implementation bug)

### False Positives

Not all R-value matches indicate vulnerability:
- Different private keys can legitimately use same R-value
- Must verify signatures are from same key
- Additional analysis needed to confirm exploitability

## Example Output

### Normal Scanning

```
[INFO] Bitcoin Transaction Weakness Scanner
[INFO] Starting scan from block 934019 down to 933969
[INFO] Scanning block 934019
[INFO] Block 934019 hash: 00000000000000000001a2b3c4d5e6f7...
[INFO] Block 934019 header retrieved successfully
[INFO] Scan complete. Processed 50 blocks.
[INFO] R-values tracked: 15234
```

### Weakness Detected

```
[ALERT] R-VALUE REUSE DETECTED!
[ALERT] R-value: 00abcdef1234567890abcdef1234567890...
[ALERT] Used in 2 different signatures:
[ALERT]   - Transaction: abc123..., Input: 0
[ALERT]   - Transaction: def456..., Input: 1
[INFO] Weakness saved to found_weaknesses_daily.txt
```

## Troubleshooting

### Connection Issues

```
[ERROR] Electrum request failed: [Errno -5] No address associated with hostname
```

**Solution**: Check Electrum server address and port:
```python
ELECTRUM_SERVER_ALT = ('electrum.blockstream.info', 50001)
```

Try alternative servers:
- `('fortress.qtornado.com', 50001)`
- `('bitcoin.lukechilds.co', 50001)`
- `('electrum.coinucopia.io', 50001)`

### Timeout Errors

```
[ERROR] Electrum request timed out
```

**Solution**: Increase timeout:
```python
with socket.create_connection(server_addr, timeout=30) as s:
    s.settimeout(30)
```

### No Transactions Found

```
[ERROR] No transactions found in block
```

**Note**: This is a known limitation of the Electrum protocol. Full transaction enumeration requires additional RPC methods or Bitcoin Core access.

## Advanced Usage

### Continuous Monitoring

Run scanner in a loop:

```bash
while true; do
    python3 scan_btc_weakness.py
    sleep 600  # 10 minutes between runs
done
```

### Systemd Service

Create `/etc/systemd/system/btc-weakness-scanner.service`:

```ini
[Unit]
Description=Bitcoin Weakness Scanner
After=network.target

[Service]
Type=simple
User=bitcoin
WorkingDirectory=/opt/Electrum-seed
ExecStart=/usr/bin/python3 scan_btc_weakness.py
Restart=always
RestartSec=600

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable btc-weakness-scanner
sudo systemctl start btc-weakness-scanner
```

### Custom Analysis

Extend the scanner for custom analysis:

```python
from scan_btc_weakness import (
    extract_r_from_der_signature,
    analyze_transaction_simple,
    r_value_database
)

# Your custom logic
def custom_analysis(tx_hex, txid):
    r_values = analyze_transaction_simple(tx_hex, txid)
    # Add custom checks here
    return r_values
```

## Contributing

Contributions welcome! Areas for improvement:

1. **Transaction Enumeration**: Better methods for getting block transactions
2. **Performance**: Optimize signature parsing
3. **Storage**: Database backend for R-value tracking
4. **Analysis**: More sophisticated vulnerability detection
5. **Reporting**: Enhanced output formats (JSON, CSV)

## References

- [ECDSA Signature Scheme](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [Bitcoin Transaction Format](https://en.bitcoin.it/wiki/Transaction)
- [DER Encoding](https://en.wikipedia.org/wiki/X.690#DER_encoding)
- [Electrum Protocol](https://electrumx.readthedocs.io/en/latest/protocol.html)
- [Bitcoin Core RPC](https://developer.bitcoin.org/reference/rpc/)

## License

MIT License - See LICENSE file for details.

## Disclaimer

This tool is for security research and educational purposes. Users are responsible for complying with applicable laws and using this tool ethically and responsibly.
