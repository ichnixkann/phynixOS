#!/usr/bin/env bash
# PHYNIX Copilot Completion Generator
# Generates bash and fish shell completions

set -e

OUTPUT_DIR="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Generating shell completions..."

# Create output directories
mkdir -p "$OUTPUT_DIR"/bash
mkdir -p "$OUTPUT_DIR"/fish/conf.d

# Generate using Python module
python3 - "$OUTPUT_DIR" << 'PYTHON'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1].rsplit('/', 1)[0])
from completions import CompletionGenerator

output_dir = Path(sys.argv[1])
gen = CompletionGenerator()
files = gen.generate_completion_files(output_dir)

print(f"✓ Bash completion: {files['bash']}")
print(f"✓ Fish completion: {files['fish']}")
print(f"✓ Fish functions: {files['functions']}")
PYTHON

echo "✓ Completions generated in $OUTPUT_DIR"
echo ""
echo "To install:"
echo "  Bash: source $OUTPUT_DIR/bash/pcopilot.bash"
echo "  Fish: source $OUTPUT_DIR/fish/pcopilot.fish"
