# Test uv tool install method
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    git \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Test uv tool install
RUN uv tool install kimigas

# Verify installation
RUN which kimi && kimi --version

# Test the new run claude command
RUN kimi run claude --help

# Cleanup
RUN uv tool uninstall kimigas

CMD ["echo", "uv install test passed"]
