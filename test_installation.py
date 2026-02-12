#!/usr/bin/env python3
"""
Test script to validate duckframework package installation.

This script verifies that:
1. The package can be installed
2. The 'duck' command is available
3. Key commands work correctly
4. Tests can be run successfully
"""
import subprocess
import sys
import os


def run_command(cmd, description, check=True, timeout=120):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.returncode == 0:
            print(f"✓ SUCCESS: {description}")
            return True
        else:
            print(f"✗ FAILED: {description}")
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ TIMEOUT: {description} took too long")
        return False
    except subprocess.CalledProcessError as e:
        print(f"✗ ERROR: {description}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"✗ EXCEPTION: {description}")
        print(f"Error: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("DUCKFRAMEWORK PACKAGE INSTALLATION TEST")
    print("=" * 60)
    
    results = []
    
    # Test 1: Check if duck command is available
    results.append(run_command(
        ["duck", "--version"],
        "Check duck command version"
    ))
    
    # Test 2: Check duck help
    results.append(run_command(
        ["duck", "--help"],
        "Check duck help command"
    ))
    
    # Test 3: Check if duck can be run as a module
    results.append(run_command(
        [sys.executable, "-m", "duck", "--version"],
        "Check duck module execution"
    ))
    
    # Test 4: Run duck runtests
    # Note: This test might take longer, so we have a higher timeout
    print("\n" + "=" * 60)
    print("Running duck tests (this may take a while)...")
    print("=" * 60)
    
    results.append(run_command(
        ["duck", "runtests"],
        "Run duck test suite",
        timeout=300  # 5 minutes timeout for tests
    ))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("\n✓ All tests PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
