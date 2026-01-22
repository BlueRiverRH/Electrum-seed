#!/usr/bin/env python3
"""
Tests for Electrum Seed Generator

Basic tests to verify core functionality of the seed generator.
"""

import sys
from electrum_seed import ElectrumSeed
from seed_utils import (
    mnemonic_to_seed, validate_seed_length, normalize_seed,
    split_seed_phrase, calculate_seed_entropy
)


def test_generate_seed():
    """Test seed generation."""
    print("Testing seed generation...")
    generator = ElectrumSeed()
    
    # Test 12-word seed
    seed_12 = generator.generate_seed(12)
    words_12 = split_seed_phrase(seed_12)
    assert len(words_12) == 12, f"Expected 12 words, got {len(words_12)}"
    assert generator.is_electrum_seed(seed_12), "Generated seed should be valid"
    print("  ✓ 12-word seed generation works")
    
    # Test 24-word seed
    seed_24 = generator.generate_seed(24)
    words_24 = split_seed_phrase(seed_24)
    assert len(words_24) == 24, f"Expected 24 words, got {len(words_24)}"
    assert generator.is_electrum_seed(seed_24), "Generated seed should be valid"
    print("  ✓ 24-word seed generation works")


def test_validate_words():
    """Test word validation."""
    print("Testing word validation...")
    generator = ElectrumSeed()
    
    # Valid words
    valid_seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    all_valid, invalid = generator.validate_words(valid_seed)
    assert all_valid, "All words should be valid"
    assert len(invalid) == 0, "Should have no invalid words"
    print("  ✓ Valid word detection works")
    
    # Invalid words
    invalid_seed = "invalid words that are not in wordlist"
    all_valid, invalid = generator.validate_words(invalid_seed)
    assert not all_valid, "Should detect invalid words"
    assert len(invalid) > 0, "Should have invalid words"
    print("  ✓ Invalid word detection works")


def test_find_similar_words():
    """Test finding similar words."""
    print("Testing similar word finding...")
    generator = ElectrumSeed()
    
    # Test with a typo
    similar = generator.find_similar_words("abandn", max_distance=1)
    assert "abandon" in similar, "Should find 'abandon' as similar to 'abandn'"
    print("  ✓ Similar word finding works")


def test_suggest_corrections():
    """Test correction suggestions."""
    print("Testing correction suggestions...")
    generator = ElectrumSeed()
    
    # Seed with typos
    seed_with_typos = "abandn abiliyt able"
    suggestions = generator.suggest_corrections(seed_with_typos)
    assert "abandn" in suggestions, "Should suggest correction for 'abandn'"
    assert "abiliyt" in suggestions, "Should suggest correction for 'abiliyt'"
    assert "able" not in suggestions, "Should not suggest correction for valid word 'able'"
    print("  ✓ Correction suggestions work")


def test_mnemonic_to_seed():
    """Test mnemonic to seed conversion."""
    print("Testing mnemonic to seed conversion...")
    
    seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    binary_seed = mnemonic_to_seed(seed)
    
    assert len(binary_seed) == 64, f"Expected 64 bytes, got {len(binary_seed)}"
    
    # Test with passphrase
    binary_seed_with_pass = mnemonic_to_seed(seed, passphrase="test")
    assert len(binary_seed_with_pass) == 64, "Should still be 64 bytes with passphrase"
    assert binary_seed != binary_seed_with_pass, "Seed with passphrase should differ"
    print("  ✓ Mnemonic to seed conversion works")


def test_seed_utilities():
    """Test utility functions."""
    print("Testing utility functions...")
    
    # Test validate_seed_length
    assert validate_seed_length("word " * 12), "12 words should be valid"
    assert validate_seed_length("word " * 24), "24 words should be valid"
    assert not validate_seed_length("word " * 10), "10 words should be invalid"
    print("  ✓ Seed length validation works")
    
    # Test normalize_seed
    seed = "  ABANDON   Abandon   abanDON  "
    normalized = normalize_seed(seed)
    assert normalized == "abandon abandon abandon", f"Expected normalized seed, got '{normalized}'"
    print("  ✓ Seed normalization works")
    
    # Test split_seed_phrase
    seed = "abandon ability able"
    words = split_seed_phrase(seed)
    assert words == ["abandon", "ability", "able"], "Should split correctly"
    print("  ✓ Seed splitting works")
    
    # Test calculate_seed_entropy
    entropy_12 = calculate_seed_entropy(12)
    assert entropy_12 == 128, f"Expected 128 bits for 12 words, got {entropy_12}"
    entropy_24 = calculate_seed_entropy(24)
    assert entropy_24 == 256, f"Expected 256 bits for 24 words, got {entropy_24}"
    print("  ✓ Entropy calculation works")


def test_edit_distance():
    """Test edit distance calculation."""
    print("Testing edit distance...")
    generator = ElectrumSeed()
    
    # Same words
    dist = generator._edit_distance("abandon", "abandon")
    assert dist == 0, "Distance between same words should be 0"
    
    # One character different
    dist = generator._edit_distance("abandon", "abandun")
    assert dist == 1, "Distance should be 1"
    
    # Multiple differences
    dist = generator._edit_distance("abandon", "ability")
    assert dist > 1, "Distance should be greater than 1"
    
    print("  ✓ Edit distance calculation works")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Running Electrum Seed Tests")
    print("=" * 70 + "\n")
    
    tests = [
        test_generate_seed,
        test_validate_words,
        test_find_similar_words,
        test_suggest_corrections,
        test_mnemonic_to_seed,
        test_seed_utilities,
        test_edit_distance,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
