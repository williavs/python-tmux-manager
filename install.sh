#!/usr/bin/env bash
# Installation script for tmux-manager

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Tmux Manager Installation ===${NC}\n"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is required but not installed.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python3 found"

# Check tmux
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}Warning: tmux is not installed. Install it with:${NC}"
    echo "  macOS: brew install tmux"
    echo "  Ubuntu/Debian: sudo apt install tmux"
    echo "  Arch: sudo pacman -S tmux"
fi

# Determine installation directory
INSTALL_DIR="${HOME}/.local/bin"
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo -e "${YELLOW}Warning: ${INSTALL_DIR} is not in your PATH${NC}"
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# Create install directory if it doesn't exist
mkdir -p "${INSTALL_DIR}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create wrapper script
WRAPPER="${INSTALL_DIR}/t"
echo "#!/usr/bin/env python3" > "${WRAPPER}"
cat "${SCRIPT_DIR}/tmux_utils.py" >> "${WRAPPER}"
echo "" >> "${WRAPPER}"
cat "${SCRIPT_DIR}/tmux-manager.py" | grep -v "from tmux_utils import" >> "${WRAPPER}"

# Make executable
chmod +x "${WRAPPER}"

echo -e "${GREEN}✓${NC} Installed to ${INSTALL_DIR}/t"

# Create config directory
CONFIG_DIR="${HOME}/.config/tmux-manager"
mkdir -p "${CONFIG_DIR}"

# Create sample config if it doesn't exist
CONFIG_FILE="${CONFIG_DIR}/projects.conf"
if [ ! -f "${CONFIG_FILE}" ]; then
    echo "# Tmux Manager - Project Root Directories" > "${CONFIG_FILE}"
    echo "# Add one directory per line. Lines starting with # are ignored." >> "${CONFIG_FILE}"
    echo "# Use ~ for home directory. Only existing directories will be used." >> "${CONFIG_FILE}"
    echo "" >> "${CONFIG_FILE}"
    echo "# Examples:" >> "${CONFIG_FILE}"
    echo "# ~/projects" >> "${CONFIG_FILE}"
    echo "# ~/workspace" >> "${CONFIG_FILE}"
    echo "# ~/dev" >> "${CONFIG_FILE}"

    echo -e "${GREEN}✓${NC} Created config file: ${CONFIG_FILE}"
    echo -e "${YELLOW}Edit this file to add your project directories${NC}"
else
    echo -e "${GREEN}✓${NC} Config file already exists: ${CONFIG_FILE}"
fi

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Usage: t"
echo ""
echo "Configure your project directories in:"
echo "  ${CONFIG_FILE}"
echo ""

# Check if already in PATH
if command -v t &> /dev/null && [ "$(command -v t)" = "${WRAPPER}" ]; then
    echo -e "${GREEN}✓${NC} Command 't' is ready to use!"
else
    echo -e "${YELLOW}Note: You may need to restart your shell or run:${NC}"
    echo "  source ~/.bashrc  # or ~/.zshrc"
fi
