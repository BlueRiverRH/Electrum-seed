# Electrum Seed Generator and Completer

The only true Electrum seed generator and completer that is fully open source. This Python code can be inserted into a cloned version of Electrum for enhanced seed management capabilities.

## Features

- **Generate New Seeds**: Create valid Electrum-compatible seed phrases (12 or 24 words)
- **Validate Seeds**: Verify if a seed phrase is a valid Electrum seed
- **Complete Partial Seeds**: Attempt to recover seeds with missing words
- **Typo Correction**: Find similar words to correct typos in seed phrases
- **Word Validation**: Check if all words are in the BIP39 wordlist
- **Seed Utilities**: Convert seeds to binary, mask for display, and more

## Installation

### Requirements

- Python 3.7 or higher
- No external dependencies required (uses only Python standard library)

### Quick Start

1. Clone this repository:
```bash
git clone https://github.com/BlueRiverRH/Electrum-seed.git
cd Electrum-seed
```

2. Run the example script:
```bash
python3 example.py
```

## Usage

### Generate a New Seed

```python
from electrum_seed import ElectrumSeed

generator = ElectrumSeed()

# Generate a 12-word seed
seed = generator.generate_seed(12)
print(f"Your new seed: {seed}")

# Generate a 24-word seed
seed_24 = generator.generate_seed(24)
print(f"Your 24-word seed: {seed_24}")
```

### Validate an Existing Seed

```python
from electrum_seed import ElectrumSeed

generator = ElectrumSeed()
seed = "your twelve word seed phrase goes here with example words"

# Check if valid
if generator.is_electrum_seed(seed):
    print("✓ Valid Electrum seed")
else:
    print("✗ Invalid seed")

# Validate words
all_valid, invalid_words = generator.validate_words(seed)
if not all_valid:
    print(f"Invalid words: {', '.join(invalid_words)}")
```

### Correct Typos in Seeds

```python
from electrum_seed import ElectrumSeed

generator = ElectrumSeed()
seed_with_typos = "abandn abiliyt able about above absent absorb abstract absurd abuse access accident"

# Get suggestions for corrections
suggestions = generator.suggest_corrections(seed_with_typos)
for word, corrections in suggestions.items():
    print(f"Did you mean '{word}' -> {corrections[0]}?")
```

### Find Similar Words

```python
from electrum_seed import ElectrumSeed

generator = ElectrumSeed()

# Find words similar to a typo
similar = generator.find_similar_words("abandn", max_distance=1)
print(f"Similar words: {', '.join(similar)}")
```

### Convert Mnemonic to Binary Seed

```python
from seed_utils import mnemonic_to_seed, seed_to_hex

seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

# Convert to binary seed
binary_seed = mnemonic_to_seed(seed)
print(f"Binary seed: {seed_to_hex(binary_seed)}")

# With passphrase
binary_seed_with_pass = mnemonic_to_seed(seed, passphrase="my secret")
print(f"Binary seed (with passphrase): {seed_to_hex(binary_seed_with_pass)}")
```

### Mask Seed for Display

```python
from seed_utils import mask_seed, format_seed_for_display

seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

# Mask certain words
masked = mask_seed(seed, [4, 5, 6], mask="****")
print(format_seed_for_display(masked))
```

## Integration with Electrum

To integrate this code into a cloned Electrum repository:

### Method 1: Drop-in Module

1. Clone the Electrum repository:
```bash
git clone https://github.com/spesmilo/electrum.git
cd electrum
```

2. Copy the seed modules into the Electrum directory:
```bash
cp /path/to/Electrum-seed/electrum_seed.py electrum/
cp /path/to/Electrum-seed/seed_utils.py electrum/
```

3. Import and use in Electrum code:
```python
from electrum_seed import ElectrumSeed
```

### Method 2: Standalone Usage

Use these modules independently for seed generation and validation without modifying Electrum:

```bash
# Generate a new seed
python3 -c "from electrum_seed import ElectrumSeed; print(ElectrumSeed().generate_seed(12))"
```

## API Reference

### ElectrumSeed Class

#### `__init__(wordlist=None)`
Initialize the seed generator with an optional custom wordlist.

#### `generate_seed(num_words=12)`
Generate a new Electrum seed phrase.
- `num_words`: Number of words (12 or 24)
- Returns: Generated seed phrase string

#### `is_electrum_seed(seed)`
Check if a seed phrase is a valid Electrum seed.
- `seed`: Seed phrase to validate
- Returns: True if valid, False otherwise

#### `validate_words(seed)`
Validate that all words in seed are in the wordlist.
- `seed`: Seed phrase to validate
- Returns: Tuple of (all_valid: bool, invalid_words: List[str])

#### `suggest_corrections(seed)`
Suggest corrections for invalid words in a seed phrase.
- `seed`: Seed phrase with potentially invalid words
- Returns: Dictionary mapping invalid words to suggested corrections

#### `find_similar_words(word, max_distance=2)`
Find words in the wordlist similar to the given word.
- `word`: Word to find matches for
- `max_distance`: Maximum edit distance
- Returns: List of similar words

#### `complete_seed(partial_seed, known_positions=None)`
Attempt to complete a partial seed phrase (demonstration only - see limitations below).
- `partial_seed`: Partial seed with missing words (use '?' for unknown)
- `known_positions`: Optional list of positions that are known correct
- Returns: List of possible valid seed completions

**Note**: This is a demonstration implementation that only searches the first 100 words of the wordlist. For real seed recovery, use specialized tools like [btcrecover](https://github.com/gurnec/btcrecover).

## Security Considerations

⚠️ **Important Security Notes:**

1. **Never share your seed phrase** with anyone
2. **Store seeds securely** - write them down on paper and keep in a safe place
3. **Verify seed backups** - always verify you've correctly written down your seed
4. **Use passphrases** - add an extra layer of security with BIP39 passphrases
5. **Generate seeds offline** - for maximum security, generate seeds on an air-gapped machine
6. **Test recovery** - before storing significant funds, test that you can recover your wallet

## Technical Details

### Electrum Seed Format

Electrum uses a modified version of BIP39 that includes version bits in the seed derivation. This ensures that seeds are:
- Compatible with Electrum wallets
- Self-identifying (standard, 2FA, or segwit)
- Using the correct derivation path

### Seed Generation Process

1. Generate cryptographically secure random entropy
2. Convert entropy to word indices using BIP39 wordlist
3. Verify the resulting seed has valid Electrum version bits
4. Repeat until a valid Electrum seed is found

### Validation Process

Seeds are validated by:
1. Checking word count (12 or 24 words)
2. Verifying all words are in the BIP39 wordlist
3. Computing HMAC-SHA512 with "Seed version" as key
4. Checking version bits match Electrum format

## Examples

See `example.py` for comprehensive examples of all features.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is open source and available under the MIT License.

## Disclaimer

This software is provided "as is" without warranty of any kind. Users are responsible for securely managing their seed phrases. The authors are not liable for any loss of funds due to improper use of this software.

**Always backup your seeds and test recovery before using for real funds.**

## Related Projects

- [Electrum Wallet](https://github.com/spesmilo/electrum) - Official Electrum Bitcoin wallet
- [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) - Bitcoin mnemonic code standard
- [bip-utils](https://github.com/ebellocchia/bip_utils) - Python library for BIP utilities

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
