import os
import shutil
import subprocess
from typing import List, Optional

PROJECT_ROOTS = [
    '/home/wv3/projects',
    '/home/wv3/v3consult',
    '/home/wv3/workspace',
    '/home/wv3/claude-code-work',
]

def list_project_dirs() -> List[str]:
    dirs: List[str] = []
    for r in PROJECT_ROOTS:
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
