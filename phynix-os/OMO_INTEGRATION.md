# Omo Ultimate Integration Guide

## 🎯 Overview

**Omo Ultimate** is an advanced code assistant integrated into PHYNIX OS for intelligent code analysis, review, and assistance.

### Key Features

- **Code Analysis** — Understand complex code patterns
- **Code Review** — Automated code review and suggestions
- **OpenCode Integration** — Native support for OpenCode framework
- **Multi-language Support** — Works with multiple programming languages
- **Context-Aware** — Understands your project structure

## 📥 Installation

Omo Ultimate is included in PHYNIX OS by default. No additional setup needed.

Verify installation:

```bash
omo-ultimate --version
omo-ultimate --help
```

## 🚀 Quick Start

### Basic Commands

```fish
# Ask Omo about code
ask-omo "explain async/await in this file"

# Review code in current directory
code-review

# Initialize Omo in project
omo-ultimate init

# Get help
omo-ultimate --help
```

### Bash Usage

```bash
omo-ultimate code "what does this function do?"
omo-ultimate analyze src/
omo-ultimate review
```

## 💡 Usage Examples

### Example 1: Understand Code

```fish
ask-omo "how does the agent routing work?"
# Omo analyzes phynix-os/pkgs/phynix-copilot/agent.py
# Returns: Detailed explanation of routing logic
```

### Example 2: Code Review

```fish
code-review
# Omo reviews all files in current directory
# Returns: Suggestions for improvements, potential bugs, etc.
```

### Example 3: OpenCode Integration

```bash
# Ask Omo to help with OpenCode project
omo-ultimate init

# Omo understands OpenCode structure
# Provides context-aware suggestions
```

### Example 4: PHYNIX-Specific Queries

```fish
# Analyze PHYNIX architecture
ask-omo "explain the WriteGate system"

# Review phase implementations
ask-omo "review Phase 3 write tools"

# Understand agent flow
ask-omo "trace the query execution path"
```

## 🔧 Advanced Configuration

### Project Initialization

```bash
cd your-project
omo-ultimate init

# Creates .omo/config.yaml
# Analyzes project structure
# Sets up optimal analysis parameters
```

### Configuration File (~/.omo/config.yaml)

```yaml
analysis:
  languages: [python, nix, rust, fish]
  depth: full
  context_lines: 10

review:
  style_guide: pep8
  security_check: true
  performance_analysis: true

integration:
  opencode: true
  vcs: git
```

### Custom Rules

Create `.omo/rules.yaml` in your project:

```yaml
rules:
  nix_style:
    enabled: true
    standards: nixfmt

  python_style:
    enabled: true
    standards: pep8, black

  security:
    enabled: true
    checks: [sql_injection, xss, command_injection]
```

## 🤖 Integration with PHYNIX Copilot

Combine Omo with PHYNIX Copilot for comprehensive code assistance:

```fish
# Ask Claude (PHYNIX) about architecture
ask-claude "design a new module"

# Ask Omo (OpenCode) to review it
code-review

# Ask Claude to refactor based on suggestions
ask-claude "refactor write_tools.py based on code review"
```

## 📊 Analysis Output

### Code Review Output

```
🔍 Code Review: phynix-os/pkgs/phynix-copilot/

✓ Python Style: PASS (pep8)
✓ Security: PASS (no critical issues)
⚠ Performance: 2 optimization opportunities
  - tools.py:45 - Consider caching subprocess calls
  - agent.py:120 - Reduce string concatenation in loops

📝 Suggestions:
  1. Add type hints to write_tools.py functions
  2. Extract repeated patterns in agent.py
  3. Add docstrings to public API
```

### Analysis Report

```
📈 PHYNIX OS Code Analysis

Architecture Score: 8.5/10
Maintainability: 8/10
Security: 9/10
Performance: 7.5/10

Files Analyzed: 15
Issues Found: 3 (0 critical, 1 medium, 2 minor)
Suggestions: 12

Recommended Actions:
1. Add comprehensive integration tests (Phase 4)
2. Increase type hint coverage
3. Document agent decision flow
```

## 🔌 Fish Shell Functions

### ask-omo

Query Omo directly from Fish shell:

```fish
ask-omo [query]

# Examples
ask-omo "explain this function"
ask-omo "find performance issues"
ask-omo "what's the complexity here"
```

### code-review

Automatic code review of current directory:

```fish
code-review

# Reviews all files in cwd
# Returns detailed suggestions
```

### ask-claude

Complementary function for PHYNIX Copilot:

```fish
ask-claude [query]

# Examples
ask-claude "design a new feature"
ask-claude "refactor this module"
```

## 📚 Integrating with PHYNIX Workflow

### Development Cycle

```
1. Write code
2. Run code-review (Omo)
3. Ask for refactoring (Claude via ask-claude)
4. Rebuild configuration (phynix-rebuild)
5. Test with PHYNIX (pcopilot)
```

### Full Example

```fish
# Start development
phynix-dev

# Write new code
vim src/new_module.py

# Review with Omo
ask-omo "review src/new_module.py"

# Get architectural advice from Claude
ask-claude "does this fit the PHYNIX architecture?"

# Refactor based on suggestions
vim src/new_module.py

# Final review
code-review

# Rebuild and test
phynix-rebuild
pcopilot --backend
```

## 🚨 Troubleshooting

### Omo Command Not Found

```fish
# Install via overlay
nix build .#omo-ultimate

# Add to PATH
set -gp PATH /root/.nix-profile/bin
```

### Configuration Issues

```bash
# Reset configuration
rm -rf ~/.omo/

# Reinitialize
omo-ultimate init

# Verify
omo-ultimate --version
```

### Integration with OpenCode

```bash
# Ensure OpenCode is available
which opencode

# Link Omo to OpenCode
omo-ultimate integrate opencode
```

## 📖 Learning Resources

- **Omo Documentation:** https://omo.dev/docs
- **OpenCode Guide:** https://opencode.dev
- **PHYNIX Integration:** See TOOLS_INTEGRATION.md

## ✨ Best Practices

1. **Run code-review before commits**
   ```fish
   code-review > review.txt
   git add review.txt
   ```

2. **Use ask-omo for complex analysis**
   ```fish
   ask-omo "analyze database transaction flow"
   ```

3. **Combine with PHYNIX Copilot**
   ```fish
   ask-claude "design based on Omo feedback"
   ```

4. **Regular architecture reviews**
   ```fish
   ask-omo "evaluate overall project health"
   ```

5. **Document findings**
   ```bash
   omo-ultimate report > analysis-$(date +%Y-%m-%d).md
   ```

---

**Omo Ultimate + PHYNIX Copilot = Complete AI-Assisted Development Environment** 🚀
