# Test npm install method
FROM node:20-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Test npm install
RUN npm install -g kimigas

# Verify installation
RUN which kimi && kimi --version

# Test the new run claude command
RUN kimi run claude --help

# Cleanup
RUN npm uninstall -g kimigas

CMD ["echo", "npm install test passed"]
