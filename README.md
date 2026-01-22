# Electrum-seed
The only true electrum seed gen / completer open source

## Overview

This repository provides tools for **Electrum wallet seed generation and recovery**. Unlike other tools that rely on BIP39 checksum validation, these programs use **Electrum's own native mnemonic logic** to generate and validate seeds.

### Key Features

- ✓ **No BIP39 checksum validation** - Uses Electrum's native validation
- ✓ **Direct Electrum integration** - Pulls from Electrum's database and wordlist
- ✓ **Seed generation** - Create new valid Electrum seeds
- ✓ **Seed recovery** - Recover seeds with mixed up or missing words
- ✓ **Multiple seed types** - Supports standard, SegWit, and 2FA seeds

## Requirements

**IMPORTANT:** These tools must be run inside a cloned Electrum repository to access Electrum's mnemonic module and wordlist.

### Installation Steps

1. **Clone Electrum:**
   ```bash
   git clone https://github.com/spesmilo/electrum.git
   cd electrum
   ```

2. **Install Electrum dependencies:**
   ```bash
   pip install -e .
   ```
   or
   ```bash
   python3 -m pip install --user -e .
   ```

3. **Clone this repository and copy the tools:**
   ```bash
   git clone https://github.com/BlueRiverRH/Electrum-seed.git
   cp Electrum-seed/*.py .
   ```

4. **Make scripts executable:**
   ```bash
   chmod +x electrum_seed_gen.py electrum_seed_recovery.py
   ```

## Tools

### 1. Electrum Seed Generator (`electrum_seed_gen.py`)

Generate new Electrum seeds or validate existing ones.

**Usage:**
```bash
python3 electrum_seed_gen.py
```

**Features:**
- Generate new seeds (12, 15, 18, 21, or 24 words)
- Support for standard, SegWit, and 2FA seed types
- Validate existing seed phrases
- Uses Electrum's native validation (not BIP39)

**Example Session:**
```
Electrum Seed Generator
============================================================

What would you like to do?
1. Generate a new seed
2. Validate an existing seed

Enter choice (1 or 2): 1

Seed Type:
1. Standard (default)
2. SegWit
3. 2FA
Enter seed type (1-3, default 1): 1

Number of words (12, 15, 18, 21, 24, default 12): 12

Generating 12-word standard seed...

============================================================
Generated Seed:
============================================================
[your generated seed will appear here]
============================================================

IMPORTANT: Write this down and keep it safe!
Anyone with this seed can access your wallet.
```

### 2. Electrum Seed Recovery Tool (`electrum_seed_recovery.py`)

Recover Electrum wallet seeds when words are forgotten or mixed up.

**Usage:**
```bash
python3 electrum_seed_recovery.py
```

**Features:**
- Recover seeds with words in wrong order
- Find missing words when position is known
- Suggest similar words for typo correction
- Works only with Electrum's validation (no BIP39)

**Recovery Modes:**

#### Mode 1: Mixed Up Word Order
When you have all the words but they're in the wrong order:

```
Recovery Mode:
1. Recover mixed up word order (all words known)
2. Find one missing word (position known)
3. Check similar words (typo help)

Enter choice (1-3): 1

Enter your seed words (in any order, space-separated):
word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12

You entered 12 words.

Seed type (standard/segwit/2fa, default standard): standard

Do you know the correct position of any words? (y/n): n

WARNING: For 12 words, there are 12! = 479,001,600 permutations!
This may take a very long time without known positions.
Continue? (yes/no): yes
```

**Tip:** If you know the position of even 2-3 words, it dramatically reduces the search space!

#### Mode 2: One Missing Word
When you have all words except one:

```
Enter choice (1-3): 2

Enter your seed words with '?' for the missing word:
abandon ability able ? accent accept achieve across act action actor actress

Missing word is at position 4

Seed type (standard/segwit/2fa, default standard): standard

Searching for missing word...
```

#### Mode 3: Find Similar Words
When you suspect a typo:

```
Enter choice (1-3): 3

Enter a word to find similar words:
abandn

Similar words in Electrum wordlist:
  - abandon
  - about
  - absence
```

## How It Works

### Electrum vs BIP39

**BIP39** uses a checksum embedded in the last word of the mnemonic. This means:
- Only specific word combinations are valid
- Random word permutations won't validate
- Requires BIP39 wordlist and checksum validation

**Electrum** uses a different approach:
- Seeds are validated by their version number (encoded in the mnemonic)
- Uses its own 1626-word list (different from BIP39's 2048 words)
- Validation happens through Electrum's `is_seed()` method
- No checksum in the traditional sense

### Why This Tool is Different

Most seed recovery tools:
- Are designed for BIP39 seeds
- Waste time validating BIP39 checksums
- Don't work with Electrum's unique validation

This tool:
- Uses Electrum's native `mnemonic.py` module
- Validates using Electrum's `is_seed()` method
- Works directly with Electrum's wordlist
- No BIP39 checksum overhead

## Performance Notes

### Complexity
- **12-word seed:** 479,001,600 permutations (12!)
- **Known positions help:** If you know 3 words are correct, search space reduces to 9! = 362,880
- **Missing word:** Only ~1,626 attempts (size of Electrum wordlist)

### Recommendations
1. **Try to remember any correct word positions** - This dramatically reduces search time
2. **Use missing word recovery** - Much faster than permutation search
3. **Check for typos first** - Use mode 3 to verify words are in wordlist
4. **Be patient** - Full 12-word permutation can take hours or days

## Security Warnings

⚠️ **IMPORTANT SECURITY CONSIDERATIONS:**

1. **Never run these tools on an internet-connected computer with your real wallet seed**
2. **Use an air-gapped (offline) computer for real seed recovery**
3. **Delete the tools after use** - Don't leave them on public computers
4. **Only use on seeds you own** - Attempting to crack others' seeds is illegal
5. **Be aware of keyloggers** - Malware can steal seeds as you type them

## Legal Notice

These tools are provided for legitimate wallet recovery purposes only. Using them to attempt to access wallets you don't own is illegal and unethical. The authors assume no liability for misuse.

## Contributing

Contributions are welcome! Please ensure:
- Code maintains compatibility with Electrum's mnemonic module
- No BIP39 dependencies are added
- Tools remain focused on Electrum seed recovery

## License

Open source - Use at your own risk

## Support

If you found this tool helpful and it recovered your wallet, consider:
- Starring this repository
- Contributing improvements
- Sharing (responsibly) with others who need it

---

**Remember:** These tools must be run from within a cloned Electrum repository!
