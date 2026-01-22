#!/usr/bin/env python3
"""
Electrum Seed Recovery Tool
Helps recover Electrum wallet seeds when words are forgotten or mixed up.
Must be run in a cloned Electrum repository.
"""

import sys
import itertools
import hashlib
from typing import List, Optional, Set

# This script must be run from within an Electrum clone
try:
    from electrum import mnemonic
    ELECTRUM_AVAILABLE = True
except ImportError:
    ELECTRUM_AVAILABLE = False
    print("WARNING: Electrum module not found.")


class ElectrumSeedRecovery:
    """Recover Electrum seeds with missing or mixed up words"""
    
    def __init__(self):
        if not ELECTRUM_AVAILABLE:
            raise ImportError("Electrum module not available. Run from Electrum directory.")
        self.mnemonic = mnemonic.Mnemonic('en')
        self.wordlist = self.mnemonic.wordlist
    
    def normalize_seed(self, seed: str) -> str:
        """Normalize seed phrase"""
        return ' '.join(seed.lower().split())
    
    def is_valid_seed(self, seed: str, seed_type: str = 'standard') -> bool:
        """Check if seed is valid"""
        try:
            return self.mnemonic.is_seed(seed, prefix=seed_type)
        except:
            return False
    
    def recover_mixed_order(self, words: List[str], known_positions: dict = None, 
                           seed_type: str = 'standard', max_attempts: int = 1000000) -> List[str]:
        """
        Recover seed when words are in wrong order.
        
        Args:
            words: List of seed words (may be in wrong order)
            known_positions: Dict of {position: word} for words with known positions (0-indexed)
            seed_type: Type of seed to look for
            max_attempts: Maximum permutations to try
        
        Returns:
            List of valid seed phrases found
        """
        print(f"Attempting to recover seed with {len(words)} words...")
        print(f"Seed type: {seed_type}")
        
        if known_positions is None:
            known_positions = {}
        
        # Normalize all words
        words = [w.lower().strip() for w in words]
        
        # Validate all words are in wordlist
        invalid_words = [w for w in words if w not in self.wordlist]
        if invalid_words:
            print(f"WARNING: These words are not in Electrum wordlist: {invalid_words}")
            print("They may be typos or from a different wordlist (e.g., BIP39)")
            return []
        
        # Build list of positions to permute
        fixed_positions = set(known_positions.keys())
        free_positions = [i for i in range(len(words)) if i not in fixed_positions]
        free_words = [w for i, w in enumerate(words) if i not in fixed_positions]
        
        valid_seeds = []
        attempts = 0
        
        print(f"Searching through permutations...")
        print(f"Fixed positions: {len(fixed_positions)}, Free positions: {len(free_positions)}")
        
        # If all positions are free, this is just all permutations
        if not known_positions:
            for perm in itertools.permutations(words):
                if attempts >= max_attempts:
                    print(f"\nReached maximum attempts ({max_attempts})")
                    break
                
                attempts += 1
                if attempts % 10000 == 0:
                    print(f"Tried {attempts} combinations...")
                
                seed_phrase = ' '.join(perm)
                if self.is_valid_seed(seed_phrase, seed_type):
                    print(f"\n✓ FOUND VALID SEED!")
                    valid_seeds.append(seed_phrase)
        else:
            # Build seed with fixed positions
            for perm in itertools.permutations(free_words):
                if attempts >= max_attempts:
                    print(f"\nReached maximum attempts ({max_attempts})")
                    break
                
                attempts += 1
                if attempts % 10000 == 0:
                    print(f"Tried {attempts} combinations...")
                
                # Construct full seed with fixed and permuted words
                result = [''] * len(words)
                for pos, word in known_positions.items():
                    result[pos] = word
                
                perm_idx = 0
                for i in free_positions:
                    result[i] = perm[perm_idx]
                    perm_idx += 1
                
                seed_phrase = ' '.join(result)
                if self.is_valid_seed(seed_phrase, seed_type):
                    print(f"\n✓ FOUND VALID SEED!")
                    valid_seeds.append(seed_phrase)
        
        print(f"\nTotal attempts: {attempts}")
        print(f"Valid seeds found: {len(valid_seeds)}")
        
        return valid_seeds
    
    def recover_missing_word(self, partial_seed: List[str], missing_position: int,
                            seed_type: str = 'standard') -> List[str]:
        """
        Recover seed with one missing word.
        
        Args:
            partial_seed: List of words with None at missing position
            missing_position: Index of missing word (0-indexed)
            seed_type: Type of seed
        
        Returns:
            List of valid seed phrases found
        """
        print(f"Attempting to find missing word at position {missing_position + 1}...")
        
        valid_seeds = []
        attempts = 0
        
        # Try each word in wordlist
        for word in self.wordlist:
            attempts += 1
            if attempts % 100 == 0:
                print(f"Tried {attempts}/{len(self.wordlist)} words...")
            
            test_seed = partial_seed.copy()
            test_seed[missing_position] = word
            seed_phrase = ' '.join(test_seed)
            
            if self.is_valid_seed(seed_phrase, seed_type):
                print(f"\n✓ FOUND: Missing word is '{word}'")
                valid_seeds.append(seed_phrase)
        
        print(f"\nTotal attempts: {attempts}")
        print(f"Valid seeds found: {len(valid_seeds)}")
        
        return valid_seeds
    
    def suggest_similar_words(self, word: str, max_suggestions: int = 5) -> List[str]:
        """Suggest words similar to input (for typos)"""
        word = word.lower()
        
        # Exact match
        if word in self.wordlist:
            return [word]
        
        # Find words with similar start
        suggestions = []
        for w in self.wordlist:
            if w.startswith(word[:3]) and w != word:
                suggestions.append(w)
        
        return suggestions[:max_suggestions]


def main():
    """Main entry point"""
    if not ELECTRUM_AVAILABLE:
        print("\nERROR: Cannot proceed without Electrum module.")
        print("\nTo use this tool:")
        print("1. Clone Electrum: git clone https://github.com/spesmilo/electrum.git")
        print("2. cd electrum")
        print("3. Copy this script into the Electrum directory")
        print("4. Run: python3 electrum_seed_recovery.py")
        sys.exit(1)
    
    print("=" * 60)
    print("Electrum Seed Recovery Tool")
    print("=" * 60)
    print()
    print("This tool helps recover Electrum seeds when:")
    print("  - Words are in the wrong order (mixed up)")
    print("  - One word is missing or unknown")
    print("  - You're not sure about the word order")
    print()
    print("Note: This tool does NOT use BIP39 checksum validation.")
    print("It uses Electrum's own validation logic.")
    print("=" * 60)
    print()
    
    recovery = ElectrumSeedRecovery()
    
    print("Recovery Mode:")
    print("1. Recover mixed up word order (all words known)")
    print("2. Find one missing word (position known)")
    print("3. Check similar words (typo help)")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        print("\nEnter your seed words (in any order, space-separated):")
        seed_input = input().strip()
        words = seed_input.split()
        
        print(f"\nYou entered {len(words)} words.")
        
        # Ask about seed type
        seed_type = input("Seed type (standard/segwit/2fa, default standard): ").strip() or 'standard'
        
        # Ask about known positions
        has_known = input("Do you know the correct position of any words? (y/n): ").strip().lower()
        known_positions = {}
        
        if has_known == 'y':
            print("Enter known positions (format: position=word, e.g., 1=abandon)")
            print("Position is 1-indexed (first word is 1)")
            print("Enter 'done' when finished:")
            while True:
                entry = input("> ").strip()
                if entry.lower() == 'done':
                    break
                if '=' in entry:
                    try:
                        pos_str, word = entry.split('=', 1)
                        pos = int(pos_str) - 1  # Convert to 0-indexed
                        known_positions[pos] = word.strip().lower()
                    except:
                        print("Invalid format, use: position=word")
        
        print("\nWARNING: For 12 words, there are 12! = 479,001,600 permutations!")
        print("This may take a very long time without known positions.")
        confirm = input("Continue? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Cancelled.")
            sys.exit(0)
        
        print("\nStarting recovery...")
        valid_seeds = recovery.recover_mixed_order(words, known_positions, seed_type)
        
        if valid_seeds:
            print("\n" + "=" * 60)
            print("VALID SEEDS FOUND:")
            print("=" * 60)
            for i, seed in enumerate(valid_seeds, 1):
                print(f"\n{i}. {seed}")
            print("=" * 60)
        else:
            print("\nNo valid seeds found. Possible issues:")
            print("  - Incorrect words (typos)")
            print("  - Wrong seed type")
            print("  - Not an Electrum seed (maybe BIP39?)")
    
    elif choice == '2':
        print("\nEnter your seed words with '?' for the missing word:")
        print("Example: abandon ability able ? accent accept")
        seed_input = input().strip()
        words = seed_input.split()
        
        if '?' not in words:
            print("Error: No missing word marker '?' found")
            sys.exit(1)
        
        missing_position = words.index('?')
        print(f"\nMissing word is at position {missing_position + 1}")
        
        seed_type = input("Seed type (standard/segwit/2fa, default standard): ").strip() or 'standard'
        
        print("\nSearching for missing word...")
        valid_seeds = recovery.recover_missing_word(words, missing_position, seed_type)
        
        if valid_seeds:
            print("\n" + "=" * 60)
            print("VALID SEEDS FOUND:")
            print("=" * 60)
            for i, seed in enumerate(valid_seeds, 1):
                print(f"\n{i}. {seed}")
            print("=" * 60)
        else:
            print("\nNo valid seeds found.")
    
    elif choice == '3':
        print("\nEnter a word to find similar words:")
        word = input().strip()
        
        suggestions = recovery.suggest_similar_words(word)
        
        if suggestions:
            print(f"\nSimilar words in Electrum wordlist:")
            for w in suggestions:
                print(f"  - {w}")
        else:
            print(f"\nNo similar words found for '{word}'")
    
    else:
        print("Invalid choice")
        sys.exit(1)


if __name__ == '__main__':
    main()
