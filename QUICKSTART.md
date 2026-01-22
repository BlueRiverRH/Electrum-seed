# Quick Start Guide

## Setup (One-Time)

```bash
# 1. Clone Electrum
git clone https://github.com/spesmilo/electrum.git
cd electrum

# 2. Install Electrum dependencies
pip install -e .

# 3. Get the recovery tools
git clone https://github.com/BlueRiverRH/Electrum-seed.git
cp Electrum-seed/*.py .

# 4. Make executable
chmod +x electrum_seed_gen.py electrum_seed_recovery.py
```

## Usage Examples

### Generate a New Seed

```bash
python3 electrum_seed_gen.py
# Choose option 1, select seed type and word count
```

### Validate a Seed

```bash
python3 electrum_seed_gen.py
# Choose option 2, paste your seed
```

### Recover Mixed Up Words (All Words Known)

```bash
python3 electrum_seed_recovery.py
# Choose option 1
# Enter all your words in any order
# Specify any known positions to speed up recovery
```

### Find One Missing Word

```bash
python3 electrum_seed_recovery.py
# Choose option 2
# Enter seed with '?' where word is missing
# Example: word1 word2 word3 ? word5 word6 word7 word8 word9 word10 word11 word12
```

### Check for Typos

```bash
python3 electrum_seed_recovery.py
# Choose option 3
# Enter the word you're unsure about
# Get list of similar valid words
```

## Tips for Faster Recovery

### If Words Are Mixed Up:
1. **Try to remember ANY correct positions** - Even 1-2 correct positions help enormously
2. **Start with the first and last words** - These are often remembered
3. **Group words by similarity** - This can trigger memory

### If a Word is Missing:
1. **Try to narrow down the position** - Check surrounding words for context
2. **Consider common words** - Some words appear more frequently in seeds

### If You Have Typos:
1. **Use mode 3 to check each word** - Quickly identifies invalid words
2. **Focus on words that "look wrong"**
3. **Check similar-sounding words**

## Common Issues

### "Electrum module not found"
- **Cause:** Not running from Electrum directory
- **Solution:** Make sure you're in the `electrum` directory and have run `pip install -e .`

### "No valid seeds found"
- **Possible causes:**
  - Wrong seed type (try standard/segwit/2fa)
  - Typos in words (use mode 3 to check)
  - It's a BIP39 seed, not Electrum
  - Not all words are from the Electrum wordlist

### Taking Too Long
- **For mixed words:** Specify known positions to reduce search space
- **For 12+ words:** Consider running overnight or using a faster computer
- **Alternative:** Try finding one missing word at a time instead of permutations

## Performance Examples

| Scenario | Approximate Time |
|----------|-----------------|
| Find 1 missing word | ~1 second |
| 12 words, 3 known positions | Minutes to hours |
| 12 words, 0 known positions | Hours to days |
| Check word similarity | Instant |

## Safety Checklist

Before using for real recovery:

- [ ] Running on offline/air-gapped computer
- [ ] No network connection
- [ ] No malware/keyloggers (clean OS install preferred)
- [ ] Verified scripts are from official source
- [ ] Will delete scripts after use
- [ ] Have secure way to transfer recovered seed to wallet

## Next Steps After Recovery

Once you've recovered your seed:

1. **Write it down immediately** - Use pen and paper
2. **Verify it works** - Import into Electrum to check
3. **Create backup** - Store in multiple secure locations
4. **Delete recovery tools** - Remove from computer
5. **Secure the backup** - Fireproof safe, safety deposit box, etc.

---

**Need help?** Check the main README.md for detailed documentation.
