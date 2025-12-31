#!/bin/bash
#
# Quick dependency fix script for Capcat
# Handles common virtual environment and dependency issues
#
# Usage: ./scripts/fix_dependencies.sh [options]
# Options:
#   --force    Force complete rebuild
#   --check    Only check dependencies
#   --help     Show this help

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[38;5;157m'
YELLOW='\033[38;5;166m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Helper functions
log_info() {
    echo -e "${GREEN}INFO:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

log_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

show_help() {
    echo "Capcat Dependency Fix Script"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  --force    Force complete virtual environment rebuild"
    echo "  --check    Only check dependencies, don't fix"
    echo "  --help     Show this help message"
    echo
    echo "Examples:"
    echo "  $0                 # Fix dependencies automatically"
    echo "  $0 --force        # Force rebuild everything"
    echo "  $0 --check        # Only validate current state"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    log_info "Python 3 available: $(python3 --version)"
}

# Check if enhanced dependency script exists
check_enhanced_script() {
    local setup_script="$SCRIPT_DIR/setup_dependencies.py"
    if [[ -f "$setup_script" ]]; then
        echo "$setup_script"
        return 0
    else
        log_warning "Enhanced dependency script not found, using basic fix"
        return 1
    fi
}

# Basic dependency fix (fallback)
basic_fix() {
    local venv_dir="$BASE_DIR/venv"
    local requirements_file="$BASE_DIR/requirements.txt"

    log_info "Running basic dependency fix..."

    # Remove broken venv if it exists
    if [[ -d "$venv_dir" ]]; then
        log_warning "Removing existing virtual environment..."
        rm -rf "$venv_dir"
    fi

    # Create new venv
    log_info "Creating new virtual environment..."
    cd "$BASE_DIR"
    python3 -m venv venv

    # Install dependencies if requirements.txt exists
    if [[ -f "$requirements_file" ]]; then
        log_info "Installing dependencies..."
        source venv/bin/activate
        pip install -r requirements.txt
        log_info "Dependencies installed successfully"
    else
        log_warning "No requirements.txt found"
    fi
}

# Enhanced dependency fix using Python script
enhanced_fix() {
    local setup_script="$1"
    local force_flag="$2"

    log_info "Running enhanced dependency setup..."

    local cmd="python3 '$setup_script'"
    if [[ "$force_flag" == "--force" ]]; then
        cmd="$cmd --force-rebuild"
    fi

    if eval "$cmd"; then
        log_info "Enhanced dependency setup completed successfully"
        return 0
    else
        log_error "Enhanced setup failed, falling back to basic fix"
        return 1
    fi
}

# Main execution
main() {
    local force_flag=""
    local check_only=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                force_flag="--force"
                shift
                ;;
            --check)
                check_only=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    log_info "Starting Capcat dependency fix..."

    # Check Python availability
    check_python

    # If check-only mode, just run validation
    if [[ "$check_only" == true ]]; then
        if enhanced_script=$(check_enhanced_script); then
            python3 "$enhanced_script" --check-only
        else
            log_info "Basic check: Looking for virtual environment..."
            local venv_dir="$BASE_DIR/venv"
            if [[ -d "$venv_dir" ]] && [[ -f "$venv_dir/bin/python" ]]; then
                log_info "Virtual environment exists"
            else
                log_warning "Virtual environment missing or broken"
                exit 1
            fi
        fi
        exit 0
    fi

    # Try enhanced fix first
    if enhanced_script=$(check_enhanced_script); then
        if ! enhanced_fix "$enhanced_script" "$force_flag"; then
            basic_fix
        fi
    else
        basic_fix
    fi

    log_info "Dependency fix completed!"
    log_info "You can now run: ./capcat list sources"
}

# Run main function with all arguments
main "$@"