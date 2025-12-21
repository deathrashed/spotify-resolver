#!/bin/bash
#
# Installation script for Spotify Album Resolver
#
# This script installs dependencies and sets up the Spotify album resolver.
# Safe to run multiple times (idempotent).
#
# Version: 1.0.0
# Author: cursor
# Created: December 23rd, 2025

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
SRC_DIR="${PROJECT_ROOT}/src"
SCRIPT_NAME="spotify-album-resolver.py"
SCRIPT_PATH="${SRC_DIR}/${SCRIPT_NAME}"

# Configuration
CONFIG_DIR="${HOME}/.config/spotify-resolver"
LOG_DIR="${HOME}/.local/log/spotify-resolver"
PYTHON_PACKAGES=("requests" "pyperclip")

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    log_info "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        log_error "Please install Python 3 first"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    log_success "Python ${PYTHON_VERSION} found"

    # Check if python3 is in PATH and executable
    PYTHON_PATH=$(which python3)
    log_info "Python path: ${PYTHON_PATH}"
}

install_python_packages() {
    log_info "Installing Python packages..."

    for package in "${PYTHON_PACKAGES[@]}"; do
        log_info "Checking ${package}..."

        if python3 -c "import ${package}" 2>/dev/null; then
            log_success "${package} is already installed"
        else
            log_info "Installing ${package}..."
            if python3 -m pip install --user "${package}" --quiet; then
                log_success "${package} installed successfully"
            else
                log_error "Failed to install ${package}"
                exit 1
            fi
        fi
    done
}

create_directories() {
    log_info "Creating directories..."

    for dir in "${CONFIG_DIR}" "${LOG_DIR}"; do
        if [ ! -d "${dir}" ]; then
            mkdir -p "${dir}"
            log_success "Created directory: ${dir}"
        else
            log_info "Directory already exists: ${dir}"
        fi
    done
}

setup_config() {
    log_info "Setting up configuration..."

    CONFIG_FILE="${CONFIG_DIR}/config.json"

    if [ -f "${CONFIG_FILE}" ]; then
        log_warning "Configuration file already exists: ${CONFIG_FILE}"
        log_info "Skipping config creation (preserving existing config)"
    else
        log_info "Creating default configuration..."
        # Config file should already exist from script creation, but verify
        if [ ! -f "${CONFIG_FILE}" ]; then
            log_error "Configuration file not found at ${CONFIG_FILE}"
            log_info "Please ensure the config.json file exists"
        else
            log_success "Configuration file ready: ${CONFIG_FILE}"
        fi
    fi
}

make_executable() {
    log_info "Setting script permissions..."

    if [ -f "${SCRIPT_PATH}" ]; then
        chmod +x "${SCRIPT_PATH}"
        log_success "Made ${SCRIPT_NAME} executable"
    else
        log_error "Script not found: ${SCRIPT_PATH}"
        exit 1
    fi
}

test_installation() {
    log_info "Testing installation..."

    if [ ! -f "${SCRIPT_PATH}" ]; then
        log_error "Script not found: ${SCRIPT_PATH}"
        return 1
    fi

    if [ ! -x "${SCRIPT_PATH}" ]; then
        log_error "Script is not executable: ${SCRIPT_PATH}"
        return 1
    fi

    # Test that script can be executed and shows help
    if python3 "${SCRIPT_PATH}" --help &>/dev/null; then
        log_success "Script is executable and functional"
    else
        log_error "Script failed to execute"
        return 1
    fi
}

show_usage_info() {
    echo
    log_info "Installation complete!"
    echo
    echo "Usage examples:"
    echo "  ${SCRIPT_PATH} --band \"Metallica\" --album \"Master of Puppets\""
    echo "  ${SCRIPT_PATH} --query \"artist:Metallica album:Master of Puppets\""
    echo "  echo \"Metallica - Master of Puppets\" | ${SCRIPT_PATH}"
    echo "  ${SCRIPT_PATH}  # Interactive mode"
    echo
    echo "Configuration: ${CONFIG_DIR}/config.json"
    echo "Log file: ${LOG_DIR}/spotify-resolver.log"
    echo
    echo "For Keyboard Maestro and Raycast integration, see the documentation:"
    echo "  ${PROJECT_ROOT}/README.md"
}

# Main installation process
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Spotify Album Resolver - Installation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    check_python
    install_python_packages
    create_directories
    setup_config
    make_executable
    test_installation
    show_usage_info

    echo
    log_success "All done! The resolver is ready to use."
}

# Run main function
main
