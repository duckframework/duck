# Duck Framework - Installation and Testing Guide

This document describes how to test the Duck framework installation and verify that all components are working correctly.

## Installation

### From PyPI (Production)

```bash
pip install duckframework
```

### From Test PyPI (Testing)

```bash
pip install -i https://test.pypi.org/simple/ duckframework
```

### From Source (Development)

```bash
git clone https://github.com/duckframework/duck.git
cd duck
pip install -e .
```

## Verifying Installation

After installation, you can verify that Duck is installed correctly by running:

### 1. Check Version

```bash
duck --version
```

Expected output:
```
Duck/X.Y.Z Python/3.x.x
```
*Note: Version numbers will vary based on your installation.*

### 2. View Available Commands

```bash
duck --help
```

This will display all available Duck CLI commands including:
- `makeproject` - Create a new Duck project
- `makeblueprint` - Create a new blueprint
- `runserver` - Start the development/production server
- `runtests` - Run Duck's test suite
- `django` - Execute Django management commands
- And more...

### 3. Run as Python Module

You can also run Duck as a Python module:

```bash
python -m duck --version
```

## Running Tests

Duck includes a built-in test suite to verify core functionality.

### Run All Tests

```bash
duck runtests
```

This will run the complete test suite which includes:
- Server startup and routing tests
- Middleware behavior tests (404, CSRF protection)
- Security tests (URL attack protection)

Expected output:
```
.........
----------------------------------------------------------------------
Ran 9 tests in X.XXXs

OK
```

### Run Tests with Verbose Output

For more detailed test output:

```bash
duck runtests -v
```

## Automated Installation Testing

A comprehensive installation test script is available in the repository:

```bash
python test_installation.py
```

This script validates:
1. ✓ Duck command is available
2. ✓ Version command works
3. ✓ Help command displays correctly
4. ✓ Module execution works
5. ✓ Test suite runs successfully

Expected output:
```
============================================================
DUCKFRAMEWORK PACKAGE INSTALLATION TEST
============================================================
...
============================================================
TEST SUMMARY
============================================================

Total tests: 4
Passed: 4
Failed: 0

✓ All tests PASSED!
```

## Test Components

### Test Server (duck/tests/test_server.py)

Base test class that provides:
- Automatic server startup for testing
- Configurable test settings
- Proper cleanup after tests complete
- Random port selection to avoid conflicts

### Route Tests (duck/tests/test_routes.py)

Tests for default routes:
- Root URL ("/")
- About page ("/about")
- Contact page ("/contact")

### Middleware Tests (duck/tests/test_routes.py)

Tests for security and error handling:
- 404 responses for unknown paths
- CSRF protection on unsafe HTTP methods
- Protection against common URL-based attacks

## Troubleshooting

### Command Not Found

If `duck` command is not found after installation:

1. Check if it's in your PATH:
   ```bash
   which duck
   ```

2. Try running as a module instead:
   ```bash
   python -m duck --version
   ```

3. Ensure the installation directory is in your PATH

### Tests Hanging

If tests appear to hang, it may be due to server processes not shutting down properly. The latest version includes automatic cleanup, but you can manually kill processes if needed:

```bash
ps aux | grep duck-server
kill -9 <pid>
```

### Import Errors

If you encounter import errors:

1. Verify installation:
   ```bash
   pip show duckframework
   ```

2. Check Python version (requires Python 3.10+):
   ```bash
   python --version
   ```

3. Reinstall the package:
   ```bash
   pip uninstall duckframework
   pip install duckframework
   ```

## Continuous Integration

For CI/CD pipelines, you can use the automated test script:

```bash
# Install
pip install duckframework

# Verify installation
python test_installation.py

# Exit with appropriate code
echo $?  # Should be 0 on success
```

## Additional Resources

- Documentation: https://docs.duckframework.xyz
- GitHub Repository: https://github.com/duckframework/duck
- Issue Tracker: https://github.com/duckframework/duck/issues
- Homepage: https://duckframework.xyz
