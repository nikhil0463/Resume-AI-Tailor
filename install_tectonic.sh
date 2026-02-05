#!/bin/bash
set -e

echo "Installing Tectonic..."
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh

mkdir -p $HOME/.local/bin
mv tectonic $HOME/.local/bin/
export PATH="$HOME/.local/bin:$PATH"

echo "Tectonic installed successfully"
tectonic --version
