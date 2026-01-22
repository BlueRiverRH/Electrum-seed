#!/usr/bin/env python3
"""
Setup checker for Electrum Seed tools
Verifies that tools are running in correct environment
"""

import sys
import os


def check_environment():
    """Check if running in correct environment"""
    
    print("=" * 60)
    print("Electrum Seed Tools - Environment Check")
    print("=" * 60)
    print()
    
    checks_passed = 0
    checks_failed = 0
    
    # Check 1: Python version
    print("1. Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 6:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        checks_passed += 1
    else:
        print(f"   ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.6+)")
        checks_failed += 1
    print()
    
    # Check 2: Electrum module
    print("2. Checking for Electrum module...")
    try:
        from electrum import mnemonic
        print("   ✓ Electrum module found")
        checks_passed += 1
        
        # Check if wordlist is accessible
        try:
            m = mnemonic.Mnemonic('en')
            wordlist_size = len(m.wordlist)
            print(f"   ✓ Electrum wordlist loaded ({wordlist_size} words)")
            checks_passed += 1
        except Exception as e:
            print(f"   ✗ Cannot access Electrum wordlist: {e}")
            checks_failed += 1
    except ImportError as e:
        print("   ✗ Electrum module not found")
        print(f"   Error: {e}")
        checks_failed += 1
    print()
    
    # Check 3: Current directory
    print("3. Checking current directory...")
    cwd = os.getcwd()
    print(f"   Current directory: {cwd}")
    
    # Look for electrum directory structure
    has_electrum_structure = False
    electrum_indicators = [
        'electrum/mnemonic.py',
        'electrum/wordlist',
        'electrum/__init__.py'
    ]
    
    for indicator in electrum_indicators:
        if os.path.exists(indicator):
            has_electrum_structure = True
            break
    
    if has_electrum_structure:
        print("   ✓ Appears to be in Electrum directory")
        checks_passed += 1
    else:
        print("   ⚠ May not be in Electrum directory")
        print("   This is OK if Electrum is installed system-wide")
    print()
    
    # Check 4: Tool scripts exist
    print("4. Checking for tool scripts...")
    scripts = [
        'electrum_seed_gen.py',
        'electrum_seed_recovery.py'
    ]
    
    for script in scripts:
        if os.path.exists(script):
            print(f"   ✓ {script} found")
            checks_passed += 1
        else:
            print(f"   ✗ {script} not found")
            checks_failed += 1
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Checks passed: {checks_passed}")
    print(f"Checks failed: {checks_failed}")
    print()
    
    if checks_failed == 0:
        print("✓ Environment is correctly set up!")
        print("You can now run:")
        print("  - python3 electrum_seed_gen.py")
        print("  - python3 electrum_seed_recovery.py")
        return True
    else:
        print("✗ Environment setup incomplete")
        print()
        print("To set up correctly:")
        print("1. Clone Electrum: git clone https://github.com/spesmilo/electrum.git")
        print("2. cd electrum")
        print("3. Install: pip install -e .")
        print("4. Copy tools: cp /path/to/Electrum-seed/*.py .")
        print("5. Run: python3 setup_check.py")
        return False


if __name__ == '__main__':
    success = check_environment()
    sys.exit(0 if success else 1)
