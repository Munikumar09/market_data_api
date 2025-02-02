#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
GIT_HOOKS_DIR="$SCRIPT_DIR/../../.git/hooks"
echo $GIT_HOOKS_DIR
echo $SCRIPT_DIR
# Copy all hooks to .git/hooks directory
cp -r "$SCRIPT_DIR"/* "$GIT_HOOKS_DIR"
cd "$GIT_HOOKS_DIR" || exit 1
chmod +x pre-commit

echo "Git hooks have been set up successfully."

