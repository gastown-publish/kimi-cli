# Test curl install method
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    git \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Test curl install
RUN curl -fsSL https://raw.githubusercontent.com/gastown-publish/kimigas/main/install.sh | bash

# Verify installation
RUN which kimi && kimi --version

# Test the new run claude command (should show help without error)
RUN kimi run claude --help

# Cleanup test
RUN rm -rf ~/.kimi ~/.local/bin/kimi /usr/local/bin/kimigas

CMD ["echo", "curl install test passed"]
