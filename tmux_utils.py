import os
import shutil
import subprocess
from typing import List, Optional

def get_project_roots() -> List[str]:
    """Get project root directories, checking XDG_CONFIG_HOME or ~/.config first"""
    config_file = os.path.expanduser('~/.config/tmux-manager/projects.conf')

    # If config exists, read from it
    if os.path.exists(config_file):
        roots = []
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    expanded = os.path.expanduser(line)
                    if os.path.isdir(expanded):
                        roots.append(expanded)
        if roots:
            return roots

    # Default fallback: common project locations
    home = os.path.expanduser('~')
    default_roots = [
        os.path.join(home, 'projects'),
        os.path.join(home, 'workspace'),
        os.path.join(home, 'dev'),
        os.path.join(home, 'code'),
        os.path.join(home, 'Development'),
    ]

    # Only return directories that exist
    return [r for r in default_roots if os.path.isdir(r)]

def list_project_dirs() -> List[str]:
    dirs: List[str] = []
    for r in get_project_roots():
        if os.path.isdir(r):
            for d in os.listdir(r):
                p = os.path.join(r, d)
                if os.path.isdir(p) and not d.startswith('.'):
                    dirs.append(p)
    return sorted(dirs)

def pick_directory_fzf(candidates: List[str]) -> Optional[str]:
    if not shutil.which('fzf'):
        return None
    try:
        proc = subprocess.run(['fzf', '--prompt', 'Project> ', '--height', '80%', '--reverse'],
                              input='\n'.join(candidates), capture_output=True, text=True)
        choice = proc.stdout.strip()
        return choice or None
    except Exception:
        return None
