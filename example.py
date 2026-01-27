#!/usr/bin/env python3
"""
Example usage of the Electrum Seed Generator and Completer

This script demonstrates how to use the electrum_seed module
for various seed operations.
"""

from electrum_seed import ElectrumSeed
from seed_utils import (
    mnemonic_to_seed, seed_to_hex, format_seed_for_display,
    mask_seed, calculate_seed_entropy, estimate_combinations
)


def example_generate_seed():
    """Example: Generate a new Electrum seed."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Generate New Electrum Seed")
    print("=" * 70)
    
    generator = ElectrumSeed()
    
    # Generate 12-word seed
    print("\nGenerating 12-word seed...")
    seed_12 = generator.generate_seed(12)
    print(f"Generated seed:\n{format_seed_for_display(seed_12, 4)}")
    
    # Validate it
    is_valid = generator.is_electrum_seed(seed_12)
    print(f"\nValidation: {'✓ Valid Electrum seed' if is_valid else '✗ Invalid'}")
    
    # Calculate entropy
    entropy = calculate_seed_entropy(12)
    print(f"Entropy: {entropy} bits (128 bits entropy + 4 bits checksum)")


def example_validate_seed():
    """Example: Validate an existing seed."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Validate Seed")
    print("=" * 70)
    
    generator = ElectrumSeed()
    
    # Test with a sample seed
    test_seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    
    print(f"\nTesting seed: {test_seed}")
    
    # Validate words
    all_valid, invalid = generator.validate_words(test_seed)
    print(f"All words in wordlist: {'✓ Yes' if all_valid else '✗ No'}")
    if invalid:
        print(f"Invalid words: {', '.join(invalid)}")
    
    # Check if it's a valid Electrum seed
    is_electrum = generator.is_electrum_seed(test_seed)
    print(f"Valid Electrum seed: {'✓ Yes' if is_electrum else '✗ No'}")


def example_convert_to_binary_seed():
    """Example: Convert mnemonic to binary seed."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Convert Mnemonic to Binary Seed")
    print("=" * 70)
    
    test_seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    
    print(f"\nMnemonic: {test_seed}")
    
    # Convert to binary seed
    binary_seed = mnemonic_to_seed(test_seed)
    print(f"\nBinary seed (first 32 bytes): {seed_to_hex(binary_seed[:32])}")
    print(f"Full seed length: {len(binary_seed)} bytes")


def example_find_similar_words():
    """Example: Find similar words for typos."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Find Similar Words (Typo Correction)")
    print("=" * 70)
    
    generator = ElectrumSeed()
    
    # Test with typos
    typos = ["abandn", "abiliyt", "abov"]
    
    for typo in typos:
        print(f"\nTypo: '{typo}'")
        similar = generator.find_similar_words(typo, max_distance=2)
        if similar:
            print(f"Suggestions: {', '.join(similar[:5])}")
        else:
            print("No suggestions found")


def example_suggest_corrections():
    """Example: Suggest corrections for invalid seed."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Suggest Corrections for Invalid Seed")
    print("=" * 70)
    
    generator = ElectrumSeed()
    
    # Seed with typos
    invalid_seed = "abandn abiliyt able abov above absent absorb abstract absurd abuse access accident"
    
    print(f"\nInvalid seed: {invalid_seed}")
    
    suggestions = generator.suggest_corrections(invalid_seed)
    
    if suggestions:
        print("\nSuggested corrections:")
        for word, corrections in suggestions.items():
            print(f"  '{word}' -> {', '.join(corrections[:3])}")
    else:
        print("\n✓ All words are valid")


def example_complete_partial_seed():
    """Example: Complete a partial seed."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Complete Partial Seed")
    print("=" * 70)
    
    generator = ElectrumSeed()
    
    # Partial seed with unknown words marked as '?'
    partial_seed = "abandon ability ? about above ? absorb abstract ? abuse access accident"
    
    print(f"\nPartial seed: {partial_seed}")
    
    unknown_count = partial_seed.count('?')
    print(f"Unknown words: {unknown_count}")
    
    # Estimate combinations
    combinations = estimate_combinations(unknown_count)
    print(f"Possible combinations: {combinations:,}")
    
    print("\n⚠ Note: Completing seeds with many unknown words is computationally expensive.")
    print("This example is limited to demonstrate the concept.")
    
    # For demonstration, we'll only try a very limited search
    # In practice, you would need specialized hardware for large searches


def example_mask_seed_display():
    """Example: Mask seed for secure display."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Mask Seed for Display")
    print("=" * 70)
    
    test_seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    
    print(f"\nOriginal seed:\n{format_seed_for_display(test_seed, 4)}")
    
    # Mask middle words
    masked = mask_seed(test_seed, [4, 5, 6, 7], mask='****')
    print(f"\nMasked seed (words 5-8 hidden):\n{format_seed_for_display(masked, 4)}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + " " * 15 + "Electrum Seed Generator Examples" + " " * 20 + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        example_generate_seed()
        example_validate_seed()
        example_convert_to_binary_seed()
        example_find_similar_words()
        example_suggest_corrections()
        example_mask_seed_display()
        example_complete_partial_seed()
        
        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print("\nYou can now integrate this code into your Electrum installation.")
        print("For more information, see the README.md file.")
        print()
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
