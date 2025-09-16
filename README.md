# Python Tmux Manager 🐍

**Interactive command-line tmux session manager with safety features**

A Python-based tmux session management tool that provides safe, interactive control over tmux sessions. This is the script behind the `t` command alias - designed for quick session switching and workspace management.

## 🚀 Features

- **Interactive Session Browser** - Navigate through existing tmux sessions safely
- **Session Details** - View session info, window counts, and attachment status
- **Safe Operations** - Prevents accidental session destruction 
- **Color-coded Output** - Clear visual feedback with ANSI colors
- **Current Session Awareness** - Always knows which session you're in
- **Directory Integration** - Project directory awareness with fzf integration

## 📋 Requirements

- **Python 3.6+** - Modern Python with type hints
- **tmux** - Terminal multiplexer (tested with 3.0+)  
- **fzf** - Fuzzy finder (for directory selection)

## 🔧 Installation

### Quick Setup (Alias Method)
Add this line to your `~/.bashrc`:
```bash
alias t='python3 /path/to/tmux-manager.py'
```

### Standalone Usage
```bash
# Run directly
python3 tmux-manager.py

# Make executable and run
chmod +x tmux-manager.py
./tmux-manager.py
```

## 🎮 Usage

Simply run the `t` command:
```bash
t
```

### Interactive Interface
- **View Sessions** - See all active tmux sessions with details
- **Switch Sessions** - Safely switch between sessions
- **Session Status** - Shows attached/detached status
- **Window Counts** - See how many windows each session has
- **Creation Times** - View when sessions were created

### Safety Features
- **Non-destructive** - Focuses on session switching rather than destruction
- **Current Session Awareness** - Never loses track of your current context
- **Error Handling** - Graceful handling of tmux command failures

## 🏗️ Architecture

```
python-tmux-manager/
├── tmux-manager.py     # Main interactive session manager
├── tmux_utils.py       # Utility functions for directory/project handling
└── README.md           # This documentation
```

### Core Components

#### `TmuxManager` Class
- **Session Management** - List, switch, and monitor tmux sessions
- **Interactive Interface** - Menu-driven session selection
- **Safety Checks** - Prevents dangerous operations
- **Color Output** - Visual feedback with ANSI color codes

#### `tmux_utils.py` Module
- **Directory Listing** - Project directory discovery
- **FZF Integration** - Fuzzy finder for directory selection
- **Utility Functions** - Helper functions for tmux operations

## 🎨 Interface

The tool provides a clean, color-coded interface:

```
Current Session: my-project (3 windows, attached)

Available Sessions:
  [1] work-session     (5 windows, detached)
  [2] personal-project (2 windows, detached) 
  [3] testing-env      (1 window, detached)

Select session [1-3] or 'q' to quit:
```

## 🔗 Integration

This Python tmux manager works alongside other tmux tools:

- **`t`** - This Python manager (quick session switching)
- **`wiz`** - Bash-based tmux wizard (complex session creation)
- **`tuiwiz`** - TUI-based tmux wizard (keyboard-driven interface)

Each tool serves different use cases in a complete tmux workflow.

## 📊 Session Information

For each session, the manager displays:
- **Session Name** - Human-readable identifier
- **Window Count** - Number of windows in the session
- **Attachment Status** - Whether someone is currently attached
- **Creation Time** - When the session was originally created
- **Current Indicator** - Highlights your active session

## 🐛 Troubleshooting

### Common Issues

**"tmux error" messages:**
```bash
# Check if tmux is running
tmux list-sessions

# Verify tmux installation
which tmux
```

**Directory picker not working:**
```bash
# Ensure fzf is installed
which fzf

# Install fzf if missing
sudo apt install fzf  # Ubuntu/Debian
brew install fzf      # macOS
```

### Debug Mode
Run with Python's verbose flag to see detailed output:
```bash
python3 -v tmux-manager.py
```

## 📄 License

MIT License - Part of the WillyV3 tmux workflow suite.

## 🤝 Related Projects

- **tmux-wizard-tui** - TUI interface for tmux session creation
- **tmux-scripts** - Collection of tmux automation tools

---

**Quick Start**: Add `alias t='python3 /path/to/tmux-manager.py'` to your shell config and enjoy safe, interactive tmux session management! 🚀