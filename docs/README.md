# Directory for Duck framework Docs

This directory contains the documentation for the Duck framework, built using Sphinx with sphinx-multiversion for multi-version documentation support.

## Overview

- These docs are built with `sphinx-multiversion` to support documentation for multiple versions/tags
- Workflow file is located at `.github/workflows/docs.yml`
- Docs source is at `docs/source`
- Configuration is in `docs/source/conf.py`

## Sphinx Multiversion Setup

### Why Both Branch and Tag Triggers?

The GitHub Actions workflow **must trigger on BOTH the main branch AND tags** because:

1. **Tag triggers (`tags: ['*']`)**: Required to build documentation when new version tags are created
2. **Branch triggers (`branches: [main]`)**: Required to update documentation for the latest development version
3. **sphinx-multiversion** scans the entire git history (all branches and tags) and builds documentation for each version in a single unified build

### How It Works

1. When the workflow triggers (on push to main or when a tag is pushed):
   - Full git history is checked out (`fetch-depth: 0`)
   - sphinx-multiversion scans all branches and tags
   - Documentation is built for each version that matches the configured filters
   - All versions are compiled into a single deployable documentation site

2. Configuration in `docs/source/conf.py`:
   ```python
   smv_tag_whitelist = r'^.*$'  # Match all tags
   smv_branch_whitelist = r'^(main|stable)$'  # Match main and stable branches
   smv_remote_whitelist = r'^origin$'
   ```

### Building Locally

To build the docs locally with multiversion support:

```bash
# Install dependencies
pip install -r docs/requirements.txt
pip install .

# Build multiversion docs
sphinx-multiversion docs/source docs/build/html
```

### Important Notes

- **DO NOT remove either the tag or branch trigger** from the workflow - both are essential for sphinx-multiversion to work correctly
- The `fetch-depth: 0` setting in the checkout action is critical - it ensures the full git history is available
- Without full history, sphinx-multiversion cannot see all versions and will only build for the current commit

