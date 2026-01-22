#!/usr/bin/env python3
"""
Electrum Seed Generator
Generates valid Electrum wallet seeds using Electrum's own mnemonic logic.
Must be run in a cloned Electrum repository to access the wordlist.
"""

import sys
import os
from typing import List, Optional

# This script must be run from within an Electrum clone
# It will import Electrum's mnemonic module
try:
    from electrum import mnemonic
    ELECTRUM_AVAILABLE = True
except ImportError:
    ELECTRUM_AVAILABLE = False
    print("WARNING: Electrum module not found. This script must be run from within an Electrum repository clone.")
    print("Clone Electrum first: git clone https://github.com/spesmilo/electrum.git")
    print("Then run this script from that directory.")


class ElectrumSeedGenerator:
    """Generate valid Electrum seeds using Electrum's own logic"""
    
    def __init__(self):
        if not ELECTRUM_AVAILABLE:
            raise ImportError("Electrum module not available. Run from Electrum directory.")
        self.mnemonic = mnemonic
    
    def generate_seed(self, seed_type: str = 'standard', num_words: int = 12) -> str:
        """
        Generate a valid Electrum seed.
        
        Args:
            seed_type: Type of seed ('standard', 'segwit', '2fa')
            num_words: Number of words (12, 15, 18, 21, 24)
        
        Returns:
            A valid Electrum mnemonic seed phrase
        """
        # Use Electrum's own make_seed function
        seed = self.mnemonic.Mnemonic('en').make_seed(seed_type=seed_type, num_words=num_words)
        return seed
    
    def is_valid_seed(self, seed: str, seed_type: str = 'standard') -> bool:
        """
        Check if a seed is valid using Electrum's validation.
        
        Args:
            seed: The seed phrase to validate
            seed_type: Expected seed type
        
        Returns:
            True if valid, False otherwise
        """
        try:
            m = self.mnemonic.Mnemonic('en')
            # Electrum's is_seed method checks validity
            return m.is_seed(seed, prefix=seed_type)
        except Exception as e:
            print(f"Validation error: {e}")
            return False
    
    def normalize_seed(self, seed: str) -> str:
        """Normalize seed phrase (lowercase, single spaces)"""
        return ' '.join(seed.lower().split())


def main():
    """Main entry point for seed generation"""
    if not ELECTRUM_AVAILABLE:
        print("\nERROR: Cannot proceed without Electrum module.")
        print("\nTo use this tool:")
        print("1. Clone Electrum: git clone https://github.com/spesmilo/electrum.git")
        print("2. cd electrum")
        print("3. Copy this script into the Electrum directory")
        print("4. Run: python3 electrum_seed_gen.py")
        sys.exit(1)
    
    print("=" * 60)
    print("Electrum Seed Generator")
    print("=" * 60)
    print()
    
    generator = ElectrumSeedGenerator()
    
    # Interactive mode
    print("What would you like to do?")
    print("1. Generate a new seed")
    print("2. Validate an existing seed")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        print("\nSeed Type:")
        print("1. Standard (default)")
        print("2. SegWit")
        print("3. 2FA")
        seed_type_choice = input("Enter seed type (1-3, default 1): ").strip() or '1'
        
        seed_type_map = {'1': 'standard', '2': 'segwit', '3': '2fa'}
        seed_type = seed_type_map.get(seed_type_choice, 'standard')
        
        num_words = input("Number of words (12, 15, 18, 21, 24, default 12): ").strip() or '12'
        num_words = int(num_words)
        
        print(f"\nGenerating {num_words}-word {seed_type} seed...")
        seed = generator.generate_seed(seed_type=seed_type, num_words=num_words)
        
        print("\n" + "=" * 60)
        print("Generated Seed:")
        print("=" * 60)
        print(seed)
        print("=" * 60)
        print("\nIMPORTANT: Write this down and keep it safe!")
        print("Anyone with this seed can access your wallet.")
        
    elif choice == '2':
        print("\nEnter your seed phrase to validate:")
        seed = input().strip()
        
        seed_type_choice = input("Expected seed type (standard/segwit/2fa, default standard): ").strip() or 'standard'
        
        seed = generator.normalize_seed(seed)
        is_valid = generator.is_valid_seed(seed, seed_type=seed_type_choice)
        
        print("\n" + "=" * 60)
        if is_valid:
            print("✓ VALID: This is a valid Electrum seed!")
        else:
            print("✗ INVALID: This is not a valid Electrum seed.")
            print("It may be:")
            print("  - A BIP39 seed (use BIP39 tools instead)")
            print("  - Incorrectly typed")
            print("  - Missing or extra words")
            print("  - Words in wrong order (use seed recovery tool)")
        print("=" * 60)
    
    else:
        print("Invalid choice")
        sys.exit(1)


if __name__ == '__main__':
    main()
