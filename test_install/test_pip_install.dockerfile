# Test pip install method
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Test pip install
RUN pip install kimigas

# Verify installation
RUN which kimi && kimi --version

# Test the new run claude command
RUN kimi run claude --help

# Cleanup
RUN pip uninstall -y kimigas

CMD ["echo", "pip install test passed"]
