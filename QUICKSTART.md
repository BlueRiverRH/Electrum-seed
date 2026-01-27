# Quick Start Guide - Bitcoin Weakness Scanner

## Installation

```bash
# Clone repository
git clone https://github.com/BlueRiverRH/Electrum-seed.git
cd Electrum-seed

# No dependencies needed - pure Python!
```

## Run Scanner

```bash
# Start scanning (connects to Electrum server)
python3 scan_btc_weakness.py

# Run tests (offline demo)
python3 test_weakness_scanner.py
```

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. Connect to Electrum Server                              │
│     ↓                                                        │
│  2. Get Latest Block Height (e.g., 934019)                  │
│     ↓                                                        │
│  3. Scan Blocks Backward (934019 → 934000 → ...)           │
│     ↓                                                        │
│  4. For Each Block:                                         │
│     • Fetch block header                                    │
│     • Extract transactions                                  │
│     • Parse signature R-values                              │
│     ↓                                                        │
│  5. Track R-values in Database                              │
│     • r_value → [(txid, input_idx), ...]                   │
│     ↓                                                        │
│  6. Detect Reuse                                            │
│     • IF r_value seen before → ALERT!                       │
│     ↓                                                        │
│  7. Save Results                                            │
│     • found_weaknesses_daily.txt                            │
│     • last_processed_block.txt (checkpoint)                 │
└─────────────────────────────────────────────────────────────┘
```

## What Gets Detected

**R-Value Reuse** = Same random number (nonce) used in multiple ECDSA signatures

```python
# Example: Two signatures from same private key
sig1 = sign(message1, private_key, nonce=k)  # R = k*G
sig2 = sign(message2, private_key, nonce=k)  # R = k*G (SAME!)

# Attacker can recover private_key!
k = (z1 - z2) / (s1 - s2) mod n
private_key = (s*k - z) / r mod n
```

## Example Output

### When Weakness Found

```
[ALERT] R-VALUE REUSE DETECTED!
[ALERT] R-value: 00abcdef1234567890abcdef...
[ALERT] Used in 2 different signatures:
[ALERT]   - Transaction: abc123def456..., Input: 0
[ALERT]   - Transaction: 789xyz012345..., Input: 1
```

### Saved to File

```bash
cat found_weaknesses_daily.txt
```

```
================================================================================
R-VALUE REUSE DETECTED!
Timestamp: 2026-01-27 22:46:22
R-value: 00abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
Used in 2 signatures:
  - Transaction: tx_abc123, Input: 0
  - Transaction: tx_def456, Input: 0
================================================================================
```

## Configuration

Edit `scan_btc_weakness.py`:

```python
# Electrum server
ELECTRUM_SERVER_ALT = ('electrum.blockstream.info', 50001)

# Files
OUTPUT_FOUND = 'found_weaknesses_daily.txt'
CHECKPOINT_FILE = 'last_processed_block.txt'

# Performance
SCAN_DELAY = 1  # Seconds between blocks
MAX_BLOCKS_PER_RUN = 50  # Blocks per session
```

## Scanning Strategy

1. **Recent First**: Starts with latest blocks (today's transactions)
2. **Go Backward**: Processes older blocks as bandwidth allows
3. **Resume Capable**: Checkpoint file saves progress
4. **Continuous**: Run multiple times to scan more history

```
Run 1: Blocks 934019 → 933969 (50 blocks)
       ↓ Checkpoint: 933969
Run 2: Blocks 933968 → 933918 (50 blocks)
       ↓ Checkpoint: 933918
Run 3: Blocks 933917 → 933867 (50 blocks)
       ... and so on
```

## Files Created

```
found_weaknesses_daily.txt  # Detected vulnerabilities
last_processed_block.txt    # Resume point (e.g., "933850")
```

## Typical Usage Patterns

### One-Time Scan

```bash
python3 scan_btc_weakness.py
```

### Continuous Monitoring

```bash
# Scan every 10 minutes
while true; do
    python3 scan_btc_weakness.py
    sleep 600
done
```

### Aggressive Historical Scan

```python
# Edit scan_btc_weakness.py
SCAN_DELAY = 0.1  # Faster!
MAX_BLOCKS_PER_RUN = 500  # More blocks!
```

```bash
# Run multiple times
for i in {1..100}; do
    python3 scan_btc_weakness.py
    echo "Completed batch $i"
done
```

## Performance

| Setting | Blocks/Hour | Days/Hour | Notes |
|---------|------------|-----------|-------|
| Default (DELAY=1, MAX=50) | ~1800 | ~1.25 | Gentle on server |
| Fast (DELAY=0.1, MAX=500) | ~18000 | ~12.5 | May hit rate limits |
| Aggressive (DELAY=0, MAX=1000) | ~36000 | ~25 | Risk of ban |

*Assuming 144 blocks/day average*

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection failed | Check server address, try alternative |
| Timeout | Increase timeout in code |
| No transactions | Electrum protocol limitation (expected) |
| Rate limited | Increase SCAN_DELAY |

## Alternative Electrum Servers

```python
# Try these if default doesn't work:
('fortress.qtornado.com', 50001)
('bitcoin.lukechilds.co', 50001)
('electrum.coinucopia.io', 50001)
('ecdsa.net', 50001)
```

## Why This Matters

**Real-World Cases:**

1. **Sony PS3 (2010)**: Fixed R-value → All games cracked
2. **Android Bitcoin Wallets (2013)**: Weak RNG → $5M stolen
3. **Blockchain.info (2014)**: Poor randomness → Keys exposed
4. **Various Exchanges**: Multiple incidents of R-reuse

**Prevention:** This scanner helps identify such weaknesses in the Bitcoin blockchain.

## What To Do If You Find Something

1. **Document**: Save all details (txids, R-values, timestamps)
2. **Verify**: Confirm it's actually from same private key
3. **Research**: Investigate the root cause
4. **Report**: Consider responsible disclosure if it affects live wallets
5. **Educate**: Share findings (anonymously if needed) to improve security

## Learn More

- Full documentation: `SCANNER_GUIDE.md`
- Test suite: `python3 test_weakness_scanner.py`
- Source code: `scan_btc_weakness.py`

## Support

Questions? Issues? Contributions?
- GitHub: https://github.com/BlueRiverRH/Electrum-seed
- Issues: https://github.com/BlueRiverRH/Electrum-seed/issues

---

**Remember:** This tool is for security research and education. Use responsibly!
