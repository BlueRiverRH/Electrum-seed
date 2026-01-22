# Electrum Seed Tools - Usage Examples

This file contains practical examples of how to use the Electrum seed tools.

## Table of Contents
1. [Basic Seed Generation](#basic-seed-generation)
2. [Seed Validation](#seed-validation)
3. [Mixed Up Words Recovery](#mixed-up-words-recovery)
4. [Missing Word Recovery](#missing-word-recovery)
5. [Batch Testing](#batch-testing)
6. [Advanced Recovery Techniques](#advanced-recovery-techniques)

---

## Basic Seed Generation

### Generate a Standard 12-Word Seed

```bash
$ python3 electrum_seed_gen.py
============================================================
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
[Generated seed will appear here]
============================================================
```

### Generate a SegWit 24-Word Seed

```bash
Enter choice (1 or 2): 1
Enter seed type (1-3, default 1): 2
Number of words (12, 15, 18, 21, 24, default 12): 24
```

---

## Seed Validation

### Validate an Existing Seed

```bash
$ python3 electrum_seed_gen.py

Enter choice (1 or 2): 2

Enter your seed phrase to validate:
word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12

Expected seed type (standard/segwit/2fa, default standard): standard

============================================================
✓ VALID: This is a valid Electrum seed!
============================================================
```

### Check Invalid Seed

```bash
Enter your seed phrase to validate:
invalid word not in wordlist

============================================================
✗ INVALID: This is not a valid Electrum seed.
It may be:
  - A BIP39 seed (use BIP39 tools instead)
  - Incorrectly typed
  - Missing or extra words
  - Words in wrong order (use seed recovery tool)
============================================================
```

---

## Mixed Up Words Recovery

### Scenario 1: All Words, No Known Positions

**WARNING:** This can take a very long time!

```bash
$ python3 electrum_seed_recovery.py

Recovery Mode:
1. Recover mixed up word order (all words known)
2. Find one missing word (position known)
3. Check similar words (typo help)

Enter choice (1-3): 1

Enter your seed words (in any order, space-separated):
zoo witch walk umbrella train seven result piano music lonely keen jade

You entered 12 words.

Seed type (standard/segwit/2fa, default standard): standard

Do you know the correct position of any words? (y/n): n

WARNING: For 12 words, there are 12! = 479,001,600 permutations!
This may take a very long time without known positions.
Continue? (yes/no): yes

Starting recovery...
Tried 10000 combinations...
Tried 20000 combinations...
...
```

### Scenario 2: Some Known Positions

**MUCH FASTER!** Knowing even 2-3 positions helps dramatically.

```bash
Enter your seed words (in any order, space-separated):
zoo witch walk umbrella train seven result piano music lonely keen jade

Do you know the correct position of any words? (y/n): y

Enter known positions (format: position=word, e.g., 1=abandon)
Position is 1-indexed (first word is 1)
Enter 'done' when finished:
> 1=witch
> 5=seven
> 12=jade
> done

Starting recovery...
Searched through permutations...

✓ FOUND VALID SEED!

============================================================
VALID SEEDS FOUND:
============================================================

1. witch result train zoo seven umbrella walk music keen lonely piano jade
============================================================
```

### Scenario 3: First and Last Words Known

```bash
Do you know the correct position of any words? (y/n): y

> 1=first_word
> 12=last_word
> done

# Now only 10! = 3,628,800 permutations to check instead of 12! = 479,001,600
```

---

## Missing Word Recovery

### Find One Missing Word

**This is FAST!** Only ~1,626 possibilities to check.

```bash
$ python3 electrum_seed_recovery.py

Enter choice (1-3): 2

Enter your seed words with '?' for the missing word:
abandon ability able ? accent accept achieve across act action actor actress

Missing word is at position 4

Seed type (standard/segwit/2fa, default standard): standard

Searching for missing word...
Tried 100/1626 words...
Tried 200/1626 words...
...
Tried 450/1626 words...

✓ FOUND: Missing word is 'absorb'

============================================================
VALID SEEDS FOUND:
============================================================

1. abandon ability able absorb accent accept achieve across act action actor actress
============================================================
```

---

## Batch Testing

### Test Multiple Seeds from File

**1. Create a file with seeds to test (`my_seeds.txt`):**

```
# My potential seeds to test
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong
ability able about above absent absorb abstract absurd abuse access accident account
```

**2. Run batch tester:**

```bash
$ python3 batch_seed_test.py my_seeds.txt

============================================================
Batch Electrum Seed Tester
============================================================

Reading seeds from: my_seeds.txt
Seed type: standard

Testing 3 seed phrases...

✓ VALID: abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about

============================================================
Results: 1 valid seeds found out of 3
============================================================

Valid seeds:
  abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
```

**3. Save valid seeds to output file:**

```bash
$ python3 batch_seed_test.py my_seeds.txt --output valid_seeds.txt
Valid seeds written to: valid_seeds.txt
```

**4. Test SegWit seeds:**

```bash
$ python3 batch_seed_test.py my_seeds.txt --type segwit
```

---

## Advanced Recovery Techniques

### Technique 1: Divide and Conquer

If you have 12 words mixed up:
1. Try to identify which words go in the first half (1-6) vs second half (7-12)
2. This reduces search from 12! to roughly 6! × 6! = 518,400,000 (still large but better)
3. Or use known positions to anchor boundaries

### Technique 2: Pattern Matching

Some users remember patterns:
- "I know these 3 words are consecutive: walk umbrella train"
- This can be incorporated as known positions

### Technique 3: Iterative Missing Word Search

If multiple words are wrong:
1. Try each position as the missing word
2. For each position, find what word would make it valid
3. Compare results to see which makes sense

Example:
```bash
# Test position 1 as missing
python3 electrum_seed_recovery.py
# Enter: ? word2 word3 word4 ... word12

# Test position 2 as missing  
python3 electrum_seed_recovery.py
# Enter: word1 ? word3 word4 ... word12

# ... and so on
```

### Technique 4: Word Similarity Check

If you suspect typos:

```bash
$ python3 electrum_seed_recovery.py

Enter choice (1-3): 3

Enter a word to find similar words:
abandn

Similar words in Electrum wordlist:
  - abandon
  - about
  - absence
  - absorb
  - abstract
```

Check each suspected word:
```bash
# Check each word in your seed
abandn    -> abandon (found!)
abillity  -> ability (found!)
acount    -> account (found!)
```

### Technique 5: Progressive Known Positions

Start with what you're certain about:
1. First attempt: Only 1-2 known positions
2. If that doesn't work, try different combinations of known positions
3. Sometimes a word you thought was in position X is actually in position Y

### Technique 6: Batch Testing Variations

Create a file with all reasonable variations:

```bash
# variations.txt
word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12
word2 word1 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12
word1 word3 word2 word4 word5 word6 word7 word8 word9 word10 word11 word12
# ... etc
```

Then test them all:
```bash
python3 batch_seed_test.py variations.txt --output found.txt
```

---

## Tips for Success

### Memory Techniques
- Try writing down all possible positions for each word
- Look for patterns or mnemonics you might have used
- Consider the first and last words - often more memorable
- Think about word associations that might have influenced your choice

### Technical Optimization
- Always specify known positions - even one helps!
- Use missing word recovery when possible (it's much faster)
- Run on a fast computer or overnight for large searches
- Consider parallel testing if you have multiple theories

### Safety Reminders
- Always work offline for real seed recovery
- Never share your seed words
- Verify any recovered seed before using it
- Make multiple secure backups once recovered

---

## Troubleshooting

### "No valid seeds found"
- **Check for typos:** Use mode 3 to verify each word
- **Try different seed types:** standard/segwit/2fa
- **Verify it's Electrum:** Not all seeds are Electrum seeds
- **Check word order:** Maybe more words are in wrong positions

### "Taking too long"
- **Add known positions:** Even 1-2 help enormously
- **Try missing word mode:** If you can narrow to one position
- **Batch smaller sets:** Test subsets of possibilities
- **Use faster hardware:** Or let it run overnight

### "Electrum module not found"
- **Wrong directory:** Must be in Electrum clone directory
- **Not installed:** Run `pip install -e .` in electrum directory
- **Wrong Python:** Try python3 instead of python

---

**Remember:** Keep your seeds secure and never share them with anyone!
