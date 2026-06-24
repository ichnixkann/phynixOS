# Fish Shell Setup Guide for PHYNIX OS

## 🐠 Overview

PHYNIX OS uses **Fish** as the primary user shell with integrated support for:
- **oh-my-fish** — Plugin framework for Fish shell
- **Tide Prompt** — Modern, customizable Fish prompt
- **oh-my-openagent** — Agent framework integrating with PHYNIX Copilot

## 📥 Installation Steps

### 1. Install oh-my-fish

Run in your Fish shell:

```fish
curl https://get.oh-my.fish | fish
```

This will:
- Create `~/.local/share/omf/` directory
- Install oh-my-fish framework
- Add initialization to `~/.config/fish/config.fish`

### 2. Install Tide Prompt

```fish
omf install tide
```

Configuration (in Fish shell):
```fish
# Customize Tide appearance
set -g tide_left_prompt_items pwd git
set -g tide_right_prompt_items status cmd_duration

# Optional: set theme
omf theme -t tide
```

### 3. Install oh-my-openagent

```fish
# Clone and install oh-my-openagent plugin
cd ~/.local/share/omf/plugins
git clone https://github.com/code-yeongyu/oh-my-openagent.git
# Or via omf if it's registered:
omf install oh-my-openagent
```

Configuration:
```fish
# Enable oh-my-openagent
set -x OPENAGENT_ENABLED true

# Set API endpoint (optional)
set -x OPENAGENT_API_URL "http://localhost:8000"  # For local models
```

## 🔌 Integration with PHYNIX Copilot

### Option 1: Manual Invocation

```fish
# Launch PHYNIX Copilot TUI
pcopilot-tui

# Single query
pcopilot "search ripgrep"

# View status
phynix-status

# Enter dev shell
phynix-dev
```

### Option 2: oh-my-openagent Integration

oh-my-openagent can be configured to use PHYNIX Copilot as a backend:

```fish
# In ~/.config/fish/conf.d/oh-my-openagent.fish
set -x OPENAGENT_BACKEND "pcopilot"
set -x OPENAGENT_COMMAND "pcopilot --tui"

# Enable agent prompt (Ctrl+A by default)
```

### Option 3: Custom Functions

Add to `~/.config/fish/functions/` :

```fish
function ask-phynix
  set query $argv
  if test -z "$query"
    pcopilot-tui
  else
    pcopilot "$query"
  end
end

function phynix-install
  set pkg $argv[1]
  pcopilot "install $pkg hm"
end

function phynix-rebuild
  echo "🔄 Rebuilding..."
  sudo nixos-rebuild switch --flake .
end
```

Usage:
```fish
ask-phynix "search vim"
phynix-install "ripgrep"
phynix-rebuild
```

## 📋 PHYNIX Fish Commands

### Built-in Aliases

```fish
ll                 # exa -lah
vi                 # vim
nix-build          # nix build
nix-check          # nix flake check
dev                # nix develop
pcopilot-tui       # pcopilot --tui
pcopilot-status    # pcopilot --backend
```

### Built-in Functions

```fish
mkcd [dir]         # mkdir && cd
phynix-dev         # nix develop
phynix-rebuild     # nixos-rebuild switch
phynix-status      # Show PHYNIX status
```

## 🎨 Tide Prompt Customization

### Common Configurations

**Minimal Prompt:**
```fish
set -g tide_left_prompt_items pwd
set -g tide_right_prompt_items status
```

**Developer-Friendly:**
```fish
set -g tide_left_prompt_items \
    pwd \
    git \
    nix
set -g tide_right_prompt_items \
    status \
    cmd_duration \
    time
```

**With Colors:**
```fish
set -g tide_pwd_dir_max_depth 3
set -g tide_pwd_truncation_strategy logical
set -g tide_git_bg_color normal
set -g tide_git_color_branch green
```

View all options:
```fish
tide configure
# Interactive configuration wizard
```

## 🔧 Oh-My-Fish Plugin Management

### View Installed Plugins

```fish
omf list
```

### Install Additional Plugins

```fish
# Popular plugins
omf install pure              # Minimalist prompt
omf install fzf              # Fuzzy finder
omf install exa              # Modern ls replacement
omf install z                # Jump to directories
```

### Remove Plugins

```fish
omf remove [plugin-name]
```

## 🤖 Oh-My-Openagent Configuration

### Environment Variables

```fish
# Set in ~/.config/fish/conf.d/openagent.fish
set -x OPENAGENT_ENABLED true
set -x OPENAGENT_API_KEY "your-key"
set -x OPENAGENT_MODEL "gpt-3.5-turbo"
set -x OPENAGENT_TEMPERATURE 0.7
set -x OPENAGENT_KEYBINDING "ctrl-a"  # Trigger keybinding
```

### Custom Prompts

Create `~/.config/openagent/prompts/phynix.txt`:

```
You are PHYNIX OS Assistant.
You help with:
- NixOS configuration
- Home Manager setup
- Hyprland customization
- System maintenance

Commands available:
- pcopilot: Query PHYNIX Copilot
- nix: NixOS operations
- home-manager: HM configuration
```

### Integration with PHYNIX Copilot

Modify oh-my-openagent to delegate to PHYNIX:

```fish
# In oh-my-openagent config
function handle_openagent_query
  set query $argv[1]
  
  # Delegate to PHYNIX for system queries
  if string match -q "*nixos*" $query
    or string match -q "*package*" $query
    or string match -q "*config*" $query
    pcopilot "$query"
  else
    # Use standard OpenAI API
    openagent "$query"
  end
end
```

## 📚 Useful Resources

- **Fish Documentation:** https://fishshell.com/docs/current/
- **oh-my-fish GitHub:** https://github.com/oh-my-fish/oh-my-fish
- **Tide Prompt:** https://github.com/IlanCosman/tide
- **oh-my-openagent:** https://github.com/code-yeongyu/oh-my-openagent

## 🚨 Troubleshooting

### oh-my-fish not loading

```fish
# Check if oh-my-fish is installed
ls ~/.local/share/omf

# Manually source it
set -gx OMF_PATH ~/.local/share/omf
source $OMF_PATH/init.fish
```

### Tide not appearing

```fish
# Install tide explicitly
omf install tide

# Configure it
tide configure

# Verify it's loaded
type tide
```

### PHYNIX commands not found

```fish
# Ensure PHYNIX is in PATH
set -gp PATH /home/phynix/.local/bin

# Create symlink if needed
ln -s /home/phynix/.nix-profile/bin/pcopilot ~/.local/bin/
```

## ✅ Verification

Check that everything is working:

```fish
# Verify Fish version
fish --version

# Check oh-my-fish
omf --version

# Test Tide
tide --version

# Test PHYNIX integration
pcopilot --backend
phynix-status
```

Expected output:
```
fish, version 3.5.0
oh-my-fish 7.2.0
tide 6.1.0
LLM Backend: offline_mode
🐠 PHYNIX Status:
Pending changes: 0
Interactive mode: true
```

---

**Setup Complete!** 🎉 You now have a fully integrated Fish + oh-my-fish + Tide + PHYNIX environment.
