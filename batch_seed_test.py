#!/usr/bin/env python3
"""
Batch Electrum Seed Tester
Tests multiple seed combinations from a file
Useful for advanced recovery scenarios
"""

import sys
import argparse
from typing import List, Set

try:
    from electrum import mnemonic
    ELECTRUM_AVAILABLE = True
except ImportError:
    ELECTRUM_AVAILABLE = False
    print("ERROR: Electrum module not found.")
    sys.exit(1)


class BatchSeedTester:
    """Test multiple seed phrases efficiently"""
    
    def __init__(self):
        self.mnemonic = mnemonic.Mnemonic('en')
    
    def is_valid_seed(self, seed: str, seed_type: str = 'standard') -> bool:
        """Check if seed is valid"""
        try:
            return self.mnemonic.is_seed(seed, prefix=seed_type)
        except:
            return False
    
    def test_seeds_from_file(self, filename: str, seed_type: str = 'standard', 
                            output_file: str = None) -> List[str]:
        """
        Test seeds from a file (one per line)
        
        Args:
            filename: Input file with seeds to test
            seed_type: Seed type to validate against
            output_file: Optional file to write valid seeds
        
        Returns:
            List of valid seeds found
        """
        valid_seeds = []
        
        print(f"Reading seeds from: {filename}")
        print(f"Seed type: {seed_type}")
        print()
        
        try:
            with open(filename, 'r') as f:
                seeds = f.readlines()
        except (IOError, OSError) as e:
            print(f"Error reading file: {e}")
            return []
        
        total = len(seeds)
        print(f"Testing {total} seed phrases...")
        print()
        
        for i, seed in enumerate(seeds, 1):
            seed = seed.strip()
            if not seed or seed.startswith('#'):  # Skip empty and comments
                continue
            
            if i % 1000 == 0:
                print(f"Progress: {i}/{total} ({100*i//total}%)")
            
            if self.is_valid_seed(seed, seed_type):
                print(f"✓ VALID: {seed}")
                valid_seeds.append(seed)
        
        print()
        print("=" * 60)
        print(f"Results: {len(valid_seeds)} valid seeds found out of {total}")
        print("=" * 60)
        
        if output_file and valid_seeds:
            try:
                with open(output_file, 'w') as f:
                    for seed in valid_seeds:
                        f.write(seed + '\n')
                print(f"Valid seeds written to: {output_file}")
            except (IOError, OSError) as e:
                print(f"Error writing output file: {e}")
        
        return valid_seeds


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Batch test Electrum seed phrases from a file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test seeds from file
  python3 batch_seed_test.py seeds.txt
  
  # Test segwit seeds
  python3 batch_seed_test.py seeds.txt --type segwit
  
  # Save valid seeds to file
  python3 batch_seed_test.py seeds.txt --output valid_seeds.txt

Input file format:
  - One seed per line
  - Lines starting with # are comments
  - Empty lines are ignored
        """
    )
    
    parser.add_argument('input_file', help='File containing seed phrases to test')
    parser.add_argument('--type', choices=['standard', 'segwit', '2fa'], 
                       default='standard', help='Seed type (default: standard)')
    parser.add_argument('--output', help='Output file for valid seeds')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Batch Electrum Seed Tester")
    print("=" * 60)
    print()
    
    tester = BatchSeedTester()
    valid_seeds = tester.test_seeds_from_file(
        args.input_file, 
        seed_type=args.type,
        output_file=args.output
    )
    
    if valid_seeds:
        print("\nValid seeds:")
        for seed in valid_seeds:
            print(f"  {seed}")


if __name__ == '__main__':
    main()
