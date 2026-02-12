# Test apt (.deb) install method
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    git \
    ripgrep \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and install .deb from GitHub releases
# Note: This will test the LATEST release
RUN VERSION=$(curl -s https://api.github.com/repos/gastown-publish/kimigas/releases/latest | grep tag_name | grep -o '[0-9.]*') && \
    echo "Testing version: $VERSION" && \
    curl -LO "https://github.com/gastown-publish/kimigas/releases/latest/download/kimigas_${VERSION}_amd64.deb" && \
    dpkg -i kimigas_*.deb || apt-get install -f -y && \
    rm kimigas_*.deb

# Verify installation
RUN which kimigas && which kimi && kimigas --version

# Test the new run claude command
RUN kimigas run claude --help

# Cleanup
RUN apt-get remove -y kimigas && rm -rf /var/lib/dpkg/info/kimigas* /usr/bin/kimi /usr/bin/kimigas

CMD ["echo", "apt install test passed"]
