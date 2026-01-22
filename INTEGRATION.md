# Integration Guide: Using Electrum Seed Code with Electrum Wallet

This guide explains how to integrate the Electrum seed generator and completer code into a cloned Electrum repository.

## Method 1: Drop-in Module Integration

This method allows you to use the seed generator within Electrum's codebase.

### Step 1: Clone Electrum

```bash
git clone https://github.com/spesmilo/electrum.git
cd electrum
```

### Step 2: Copy the Seed Modules

Copy the Python modules into Electrum's main directory:

```bash
# Copy the main modules
cp /path/to/Electrum-seed/electrum_seed.py electrum/
cp /path/to/Electrum-seed/seed_utils.py electrum/
```

### Step 3: Use in Electrum Code

You can now import and use the modules in any Electrum Python file:

```python
# In any Electrum Python file
from electrum_seed import ElectrumSeed

# Generate a new seed
generator = ElectrumSeed()
new_seed = generator.generate_seed(12)

# Validate a seed
is_valid = generator.is_electrum_seed(some_seed)

# Find typos and suggest corrections
suggestions = generator.suggest_corrections(user_input_seed)
```

### Example: Adding to Electrum GUI

If you want to add seed generation to Electrum's GUI, you could modify the relevant GUI files:

```python
# Example: In electrum/gui/qt/seed_dialog.py or similar
from electrum_seed import ElectrumSeed

class SeedDialog:
    def generate_new_seed(self):
        generator = ElectrumSeed()
        seed = generator.generate_seed(12)
        return seed
    
    def validate_user_seed(self, user_input):
        generator = ElectrumSeed()
        suggestions = generator.suggest_corrections(user_input)
        if suggestions:
            # Show user the suggestions
            return suggestions
        return generator.is_electrum_seed(user_input)
```

## Method 2: Standalone Usage

Use the modules independently without modifying Electrum.

### Command Line Usage

```bash
# Generate a seed
python3 -c "from electrum_seed import ElectrumSeed; print(ElectrumSeed().generate_seed(12))"

# Validate a seed
python3 -c "from electrum_seed import ElectrumSeed; print(ElectrumSeed().is_electrum_seed('your seed here'))"

# Get suggestions for typos
python3 -c "from electrum_seed import ElectrumSeed; print(ElectrumSeed().suggest_corrections('abandn ability'))"
```

### Create a Helper Script

Create a script `electrum_seed_tool.py`:

```python
#!/usr/bin/env python3
import sys
from electrum_seed import ElectrumSeed

def main():
    if len(sys.argv) < 2:
        print("Usage: electrum_seed_tool.py [generate|validate|correct] [args...]")
        sys.exit(1)
    
    command = sys.argv[1]
    generator = ElectrumSeed()
    
    if command == "generate":
        num_words = int(sys.argv[2]) if len(sys.argv) > 2 else 12
        print(generator.generate_seed(num_words))
    
    elif command == "validate":
        seed = ' '.join(sys.argv[2:])
        is_valid = generator.is_electrum_seed(seed)
        print(f"Valid: {is_valid}")
    
    elif command == "correct":
        seed = ' '.join(sys.argv[2:])
        suggestions = generator.suggest_corrections(seed)
        for word, corrections in suggestions.items():
            print(f"{word} -> {', '.join(corrections[:3])}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

Then use it:

```bash
python3 electrum_seed_tool.py generate 12
python3 electrum_seed_tool.py validate abandon abandon abandon...
python3 electrum_seed_tool.py correct abandn abiliyt able...
```

## Method 3: As a Plugin

You could create an Electrum plugin that uses this code.

### Create Plugin Structure

```
electrum/plugins/seed_generator/
├── __init__.py
├── seed_generator.py
├── electrum_seed.py  (copy from this repo)
└── seed_utils.py     (copy from this repo)
```

### Plugin Code (`seed_generator.py`)

```python
from electrum.plugin import BasePlugin
from .electrum_seed import ElectrumSeed

class Plugin(BasePlugin):
    def __init__(self, parent, config, name):
        BasePlugin.__init__(self, parent, config, name)
        self.generator = ElectrumSeed()
    
    def generate_seed(self, num_words=12):
        return self.generator.generate_seed(num_words)
    
    def validate_seed(self, seed):
        return self.generator.is_electrum_seed(seed)
```

## Integration Points in Electrum

Here are common places where you might want to integrate this code:

### 1. Seed Generation (electrum/mnemonic.py)

Replace or supplement Electrum's existing seed generation:

```python
from electrum_seed import ElectrumSeed

def make_seed(seed_type='standard', num_bits=128):
    generator = ElectrumSeed()
    num_words = 12 if num_bits == 128 else 24
    return generator.generate_seed(num_words)
```

### 2. Seed Validation (electrum/keystore.py)

Add validation before accepting user seeds:

```python
from electrum_seed import ElectrumSeed

def validate_seed(seed):
    generator = ElectrumSeed()
    
    # Check if valid
    if not generator.is_electrum_seed(seed):
        # Suggest corrections
        suggestions = generator.suggest_corrections(seed)
        if suggestions:
            raise InvalidSeed(f"Invalid words: {suggestions}")
        else:
            raise InvalidSeed("Not a valid Electrum seed")
    
    return True
```

### 3. GUI Seed Input (electrum/gui/qt/seed_dialog.py)

Add real-time validation and suggestions:

```python
from electrum_seed import ElectrumSeed

class SeedInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.generator = ElectrumSeed()
    
    def on_seed_changed(self, text):
        seed = text.strip()
        
        # Validate as user types
        all_valid, invalid = self.generator.validate_words(seed)
        
        if not all_valid:
            # Show suggestions
            suggestions = self.generator.suggest_corrections(seed)
            self.show_suggestions(suggestions)
```

## Testing Your Integration

After integrating, test the functionality:

```python
# Test in Python console
from electrum_seed import ElectrumSeed

gen = ElectrumSeed()

# Test generation
seed = gen.generate_seed(12)
print(f"Generated: {seed}")

# Test validation
assert gen.is_electrum_seed(seed), "Generated seed should be valid"

# Test corrections
suggestions = gen.suggest_corrections("abandn ability")
print(f"Suggestions: {suggestions}")
```

## Best Practices

1. **Always validate seeds** before accepting them from users
2. **Use suggestions** to help users correct typos
3. **Generate offline** for maximum security when creating new wallets
4. **Test thoroughly** before using with real funds
5. **Keep backups** of any generated seeds

## Troubleshooting

### Import Error

If you get `ModuleNotFoundError: No module named 'electrum_seed'`:

- Ensure the files are in the correct directory
- Check that `__init__.py` exists in the directory (for packages)
- Verify your Python path includes the directory

### Validation Fails

If seeds fail validation:

- Check that the seed is properly formatted (lowercase, space-separated)
- Verify all words are from the BIP39 wordlist
- Ensure the seed has 12 or 24 words
- Use `suggest_corrections()` to identify invalid words

## Security Notes

⚠️ **Important**: 

- Never log or store seeds in plain text
- Generate seeds on secure, offline machines when possible
- Always test wallet recovery before using with real funds
- Use hardware wallets for significant amounts

## Support

For issues specific to this integration:
- Check the main README.md for API documentation
- Review example.py for usage examples
- Run test_electrum_seed.py to verify functionality

For Electrum-specific issues:
- Visit https://electrum.org/
- See https://github.com/spesmilo/electrum
