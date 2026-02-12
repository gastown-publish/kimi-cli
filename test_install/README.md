# Kimigas Install Method Tests

Docker-based tests for all Linux installation methods.

## Prerequisites

- Docker installed and running
- User has permission to run Docker commands

## Running Tests

### Run all tests:

```bash
./run_all_tests.sh
```

### Run individual tests:

```bash
# Test curl install
docker build -f test_curl_install.dockerfile -t kimigas-curl-test ..
docker run --rm kimigas-curl-test

# Test pip install
docker build -f test_pip_install.dockerfile -t kimigas-pip-test ..
docker run --rm kimigas-pip-test

# Test uv tool install
docker build -f test_uv_install.dockerfile -t kimigas-uv-test ..
docker run --rm kimigas-uv-test

# Test npm install
docker build -f test_npm_install.dockerfile -t kimigas-npm-test ..
docker run --rm kimigas-npm-test

# Test apt (.deb) install
docker build -f test_apt_install.dockerfile -t kimigas-apt-test ..
docker run --rm kimigas-apt-test
```

## What Each Test Verifies

1. **curl install** - Tests the `install.sh` script from GitHub
2. **pip install** - Tests PyPI package installation
3. **uv install** - Tests `uv tool install` method
4. **npm install** - Tests npm global package installation
5. **apt install** - Tests .deb package download and installation

Each test:
- Installs kimigas using the specific method
- Verifies `kimi` and `kimigas` commands work
- Tests the new `kimi run claude --help` command
- Cleans up after itself

## Test Results

Test logs are saved to `test_*.log` files if a test fails.
