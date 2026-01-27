#!/usr/bin/env python3
"""
Seed Utilities Module

Provides helper functions for working with Electrum seeds including
mnemonic manipulation, entropy generation, and seed phrase utilities.
"""

import hashlib
import hmac
import secrets
from typing import List, Optional


def generate_entropy(num_bytes: int = 16) -> bytes:
    """
    Generate cryptographically secure random entropy.
    
    Args:
        num_bytes: Number of random bytes to generate
        
    Returns:
        Random bytes
    """
    return secrets.token_bytes(num_bytes)


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """
    Convert mnemonic to seed using PBKDF2.
    
    This follows the BIP39/Electrum standard for seed derivation.
    
    Args:
        mnemonic: Space-separated mnemonic words
        passphrase: Optional passphrase for additional security
        
    Returns:
        64-byte seed
    """
    mnemonic_bytes = mnemonic.encode('utf-8')
    salt = ('electrum' + passphrase).encode('utf-8')
    
    # Use PBKDF2-HMAC-SHA512 with 2048 iterations (Electrum standard)
    seed = hashlib.pbkdf2_hmac('sha512', mnemonic_bytes, salt, 2048)
    return seed


def seed_to_hex(seed: bytes) -> str:
    """
    Convert seed bytes to hexadecimal string.
    
    Args:
        seed: Seed bytes
        
    Returns:
        Hexadecimal string representation
    """
    return seed.hex()


def hex_to_seed(hex_string: str) -> bytes:
    """
    Convert hexadecimal string to seed bytes.
    
    Args:
        hex_string: Hexadecimal seed string
        
    Returns:
        Seed bytes
    """
    return bytes.fromhex(hex_string)


def verify_checksum(mnemonic: str, wordlist: List[str]) -> bool:
    """
    Verify BIP39 checksum for a mnemonic.
    
    Args:
        mnemonic: Space-separated mnemonic words
        wordlist: BIP39 wordlist
        
    Returns:
        True if checksum is valid
    """
    words = mnemonic.strip().lower().split()
    
    if len(words) not in [12, 15, 18, 21, 24]:
        return False
    
    # Convert words to indices
    try:
        indices = [wordlist.index(word) for word in words]
    except ValueError:
        return False
    
    # Convert indices to binary
    binary = ''.join(format(idx, '011b') for idx in indices)
    
    # Split entropy and checksum
    checksum_length = len(words) // 3
    entropy_bits = binary[:-checksum_length]
    checksum_bits = binary[-checksum_length:]
    
    # Convert entropy to bytes
    entropy_bytes = int(entropy_bits, 2).to_bytes(len(entropy_bits) // 8, byteorder='big')
    
    # Calculate expected checksum
    hash_bytes = hashlib.sha256(entropy_bytes).digest()
    hash_bits = ''.join(format(b, '08b') for b in hash_bytes)
    expected_checksum = hash_bits[:checksum_length]
    
    return checksum_bits == expected_checksum


def split_seed_phrase(seed: str) -> List[str]:
    """
    Split a seed phrase into individual words.
    
    Args:
        seed: Seed phrase string
        
    Returns:
        List of words
    """
    return seed.strip().lower().split()


def join_seed_phrase(words: List[str]) -> str:
    """
    Join words into a seed phrase.
    
    Args:
        words: List of seed words
        
    Returns:
        Space-separated seed phrase
    """
    return ' '.join(words)


def count_unknown_words(seed: str, unknown_marker: str = '?') -> int:
    """
    Count the number of unknown words in a partial seed.
    
    Args:
        seed: Partial seed phrase
        unknown_marker: Marker for unknown words
        
    Returns:
        Count of unknown words
    """
    words = split_seed_phrase(seed)
    return sum(1 for word in words if word == unknown_marker)


def get_unknown_positions(seed: str, unknown_marker: str = '?') -> List[int]:
    """
    Get positions of unknown words in a partial seed.
    
    Args:
        seed: Partial seed phrase
        unknown_marker: Marker for unknown words
        
    Returns:
        List of positions (0-indexed) of unknown words
    """
    words = split_seed_phrase(seed)
    return [i for i, word in enumerate(words) if word == unknown_marker]


def mask_seed(seed: str, positions_to_hide: List[int], mask: str = '***') -> str:
    """
    Mask certain words in a seed phrase for display.
    
    Args:
        seed: Seed phrase
        positions_to_hide: List of positions to mask
        mask: String to use as mask
        
    Returns:
        Masked seed phrase
    """
    words = split_seed_phrase(seed)
    for pos in positions_to_hide:
        if 0 <= pos < len(words):
            words[pos] = mask
    return join_seed_phrase(words)


def calculate_seed_entropy(num_words: int) -> int:
    """
    Calculate the entropy (in bits) for a given number of words.
    
    Note: This returns the actual entropy bits, not including the checksum.
    BIP39 uses: 12 words = 128 bits entropy + 4 bits checksum
                24 words = 256 bits entropy + 8 bits checksum
    
    Args:
        num_words: Number of words in seed phrase
        
    Returns:
        Entropy in bits (excluding checksum)
    """
    # Standard BIP39 entropy (excluding checksum)
    entropy_map = {
        12: 128,
        15: 160,
        18: 192,
        21: 224,
        24: 256
    }
    return entropy_map.get(num_words, num_words * 11)  # Fallback to total bits if non-standard


def estimate_combinations(num_unknown: int, wordlist_size: int = 2048) -> int:
    """
    Estimate the number of possible combinations for unknown words.
    
    Args:
        num_unknown: Number of unknown words
        wordlist_size: Size of the wordlist
        
    Returns:
        Number of possible combinations
    """
    return wordlist_size ** num_unknown


def format_seed_for_display(seed: str, words_per_line: int = 4) -> str:
    """
    Format seed phrase for display with line breaks.
    
    Args:
        seed: Seed phrase
        words_per_line: Number of words to display per line
        
    Returns:
        Formatted seed phrase with line breaks
    """
    words = split_seed_phrase(seed)
    lines = []
    for i in range(0, len(words), words_per_line):
        line_words = words[i:i + words_per_line]
        # Add word numbers
        numbered_words = [f"{i+j+1}. {word}" for j, word in enumerate(line_words)]
        lines.append(' '.join(numbered_words))
    return '\n'.join(lines)


def validate_seed_length(seed: str, allowed_lengths: Optional[List[int]] = None) -> bool:
    """
    Validate that a seed phrase has an allowed word count.
    
    Args:
        seed: Seed phrase
        allowed_lengths: List of allowed word counts (defaults to [12, 24])
        
    Returns:
        True if length is valid
    """
    if allowed_lengths is None:
        allowed_lengths = [12, 24]
    
    words = split_seed_phrase(seed)
    return len(words) in allowed_lengths


def normalize_seed(seed: str) -> str:
    """
    Normalize a seed phrase by trimming and lowercasing.
    
    Args:
        seed: Seed phrase
        
    Returns:
        Normalized seed phrase
    """
    words = seed.strip().lower().split()
    return ' '.join(words)
