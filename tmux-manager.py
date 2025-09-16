#!/usr/bin/env python3
"""
Tmux Session Manager - Interactive safe management of tmux sessions
Helps understand tmux hierarchy and safely manage sessions without breaking workspace
"""

import subprocess
import json
import sys
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time
from tmux_utils import list_project_dirs, pick_directory_fzf

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

class TmuxManager:
    def __init__(self):
        self.sessions = []
        self.current_session = None
        self.refresh()

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def run(self, *args: str) -> str:
        try:
            r = subprocess.run(['tmux', *args], capture_output=True, text=True)
            return r.stdout.strip()
        except Exception as e:
            print(f"{Colors.RED}tmux error: {e}{Colors.RESET}")
            return ""

    def refresh(self):
        current = self.run('display-message', '-p', '#S')
        self.current_session = current or None
        sessions_raw = self.run('list-sessions', '-F', '#{session_id}:#{session_name}:#{session_attached}:#{session_windows}:#{session_created}')
        self.sessions = []
        for line in sessions_raw.split('\n'):
            if not line:
                continue
            parts = line.split(':')
            if len(parts) < 5:
                continue
            created_time = None
            if parts[4].isdigit():
                created_time = datetime.fromtimestamp(int(parts[4])).strftime('%Y-%m-%d %H:%M')
            self.sessions.append({
                'id': parts[0],
                'name': parts[1],
                'attached': parts[2] == '1',
                'windows': int(parts[3]),
                'is_current': parts[1] == self.current_session,
                'created': created_time
            })
    
    def get_windows(self, session_name: str) -> List[Dict]:
        windows_raw = self.run('list-windows', '-t', session_name, '-F', '#{window_id}:#{window_name}:#{window_active}:#{window_panes}')
        windows = []
        for line in windows_raw.split('\n'):
            if not line:
                continue
            parts = line.split(':')
            if len(parts) < 4:
                continue
            windows.append({
                'id': parts[0],
                'name': parts[1],
                'active': parts[2] == '1',
                'panes': int(parts[3])
            })
        return windows

    def get_panes(self, session_name: str, window_id: str) -> List[Dict]:
        panes_raw = self.run('list-panes', '-t', f"{session_name}:{window_id}", '-F', '#{pane_id}:#{pane_title}:#{pane_active}:#{pane_current_command}')
        panes = []
        for line in panes_raw.split('\n'):
            if not line:
                continue
            parts = line.split(':', 3)
            if len(parts) < 4:
                continue
            panes.append({
                'id': parts[0],
                'title': parts[1] if parts[1] else 'Untitled',
                'active': parts[2] == '1',
                'command': parts[3]
            })
        return panes
    
    def get_session_app_summary(self, session_name: str) -> Dict:
        """Get summary of applications running in a session"""
        app_counts = {}
        unique_apps = set()
        total_panes = 0
        
        try:
            windows = self.get_windows(session_name)
            for window in windows:
                panes = self.get_panes(session_name, window['id'].replace('@', ''))
                for pane in panes:
                    cmd = pane['command']
                    total_panes += 1
                    
                    if cmd in ['bash', 'zsh', 'sh']:
                        app_counts['shell'] = app_counts.get('shell', 0) + 1
                    elif cmd in ['vim', 'nvim', 'vi', 'nano']:
                        app_counts['editor'] = app_counts.get('editor', 0) + 1
                    elif cmd == 'claude':
                        app_counts['claude'] = app_counts.get('claude', 0) + 1
                    elif cmd in ['python', 'python3', 'ipython']:
                        app_counts['python'] = app_counts.get('python', 0) + 1
                    elif cmd in ['node', 'npm', 'bun', 'yarn']:
                        app_counts['node'] = app_counts.get('node', 0) + 1
                    elif cmd in ['lynx', 'carbonyl', 'w3m']:
                        app_counts['browser'] = app_counts.get('browser', 0) + 1
                    elif cmd == 'ranger':
                        app_counts['files'] = app_counts.get('files', 0) + 1
                    elif cmd in ['htop', 'top', 'btop']:
                        app_counts['monitor'] = app_counts.get('monitor', 0) + 1
                    elif cmd == 'docker':
                        app_counts['docker'] = app_counts.get('docker', 0) + 1
                    else:
                        if cmd and cmd.strip():
                            app_counts['other'] = app_counts.get('other', 0) + 1
                    
                    if cmd and cmd.strip():
                        unique_apps.add(cmd)
        except:
            pass
        
        return {
            'total_panes': total_panes,
            'app_counts': app_counts,
            'unique_apps': list(unique_apps)
        }
    
    def display_header(self, title: str):
        """Display a formatted header"""
        self.clear_screen()
        print(f"\n{Colors.BOLD}{Colors.CYAN}[{title}]{Colors.RESET}\n")
    
    
    def display_session_list(self, highlight_safe: bool = False) -> List[Dict]:
        """Display session list with details"""
        safe_sessions = []
        
        for i, session in enumerate(self.sessions):
            status = ""
            color = Colors.WHITE
            is_safe = True
            
            if session['is_current']:
                status = f" {Colors.GREEN}[CURRENT]{Colors.RESET}"
                color = Colors.GREEN
                is_safe = False
            elif session['attached']:
                status = f" {Colors.YELLOW}[ATTACHED]{Colors.RESET}"
                color = Colors.YELLOW
                is_safe = False
            elif session['name'] == 'workspace':
                status = f" {Colors.RED}[PROTECTED]{Colors.RESET}"
                color = Colors.RED
                is_safe = False
            else:
                status = f" {Colors.CYAN}✓{Colors.RESET}"
                safe_sessions.append(session)
            
            summary = self.get_session_app_summary(session['name'])
            app_info = []
            
            if summary['app_counts'].get('claude', 0) > 0:
                app_info.append(f"{summary['app_counts']['claude']}claude")
            if summary['app_counts'].get('python', 0) > 0:
                app_info.append(f"{summary['app_counts']['python']}py")
            if summary['app_counts'].get('node', 0) > 0:
                app_info.append(f"{summary['app_counts']['node']}js")
            if summary['app_counts'].get('editor', 0) > 0:
                app_info.append(f"{summary['app_counts']['editor']}vim")
            if summary['app_counts'].get('browser', 0) > 0:
                app_info.append(f"{summary['app_counts']['browser']}web")
            if summary['app_counts'].get('docker', 0) > 0:
                app_info.append(f"{summary['app_counts']['docker']}docker")
            
            windows = self.get_windows(session['name'])
            window_info = f"({session['windows']}w/{summary['total_panes']}p)"
            app_str = f" [{', '.join(app_info)}]" if app_info else ""
            
            print(f"{color}{i+1:2d}. {session['name']:<20} {window_info:<10}{app_str}{Colors.RESET}{status}")
        
        return safe_sessions
    
    
    def interactive_close_session(self):
        """Interactive session closing with safety check (supports multiple selections)"""
        self.display_header("CLOSE SESSION")
        safe_sessions = self.display_session_list(highlight_safe=True)
        if not safe_sessions:
            print(f"\n{Colors.GREEN}✅ No unused sessions to clean up!{Colors.RESET}")
            input("\nPress Enter...")
            return
        print(f"\nClose session #(s) (e.g. 2,4-6) or 'q': ", end='')
        choice = input().strip()
        if choice.lower() == 'q':
            return
        indices: List[int] = []
        try:
            for part in choice.split(','):
                part = part.strip()
                if '-' in part:
                    a, b = part.split('-', 1)
                    a = int(a) - 1
                    b = int(b) - 1
                    if a > b:
                        a, b = b, a
                    indices.extend(list(range(a, b + 1)))
                elif part:
                    indices.append(int(part) - 1)
        except ValueError:
            print(f"{Colors.RED}Invalid input!{Colors.RESET}")
            time.sleep(1)
            return
        indices = sorted(set(i for i in indices if 0 <= i < len(self.sessions)))
        if not indices:
            print(f"{Colors.RED}Nothing selected.{Colors.RESET}")
            time.sleep(1)
            return
        to_close = []
        for idx in indices:
            s = self.sessions[idx]
            if s['is_current'] or s['attached'] or s['name'] == 'workspace':
                continue
            to_close.append(s)
        if not to_close:
            print(f"{Colors.YELLOW}No safe sessions selected.{Colors.RESET}")
            time.sleep(1)
            return
        print("\nReview to close:")
        for s in to_close:
            windows = self.get_windows(s['name'])
            print(f"  - {s['name']} ({len(windows)} windows)")
        print("Type 'yes' to confirm: ", end='')
        confirm = input().strip()
        if confirm.lower() != 'yes':
            print("Cancelled.")
            time.sleep(1)
            return
        for s in to_close:
            result = subprocess.run(['tmux', 'kill-session', '-t', s['name']], capture_output=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Closed {s['name']}{Colors.RESET}")
            else:
                print(f"{Colors.RED}Failed {s['name']}: {result.stderr.decode()}{Colors.RESET}")
        time.sleep(1.5)
    
    def switch_to_session(self):
        """Switch to a different session"""
        self.display_header("SWITCH SESSION")
        self.display_session_list()
        
        print(f"\nSwitch to # (or 'q'): ", end='')
        choice = input().strip()
        
        if choice.lower() == 'q':
            return
        
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(self.sessions):
                return
            
            selected = self.sessions[idx]
            
            if selected['is_current']:
                print("Already there!")
                time.sleep(1)
                return
            
            subprocess.run(['tmux', 'switch-client', '-t', selected['name']])
            
        except ValueError:
            return
    
    def create_four_pane_session(self, name: str, cwd: str):
        subprocess.run(['tmux', 'new-session', '-d', '-s', name, '-c', cwd, '-n', 'Multi-View'])
        subprocess.run(['tmux', 'split-window', '-h', '-t', f'{name}:0', '-c', cwd])
        subprocess.run(['tmux', 'split-window', '-v', '-t', f'{name}:0.0', '-c', cwd])
        subprocess.run(['tmux', 'split-window', '-v', '-t', f'{name}:0.1', '-c', cwd])
        subprocess.run(['tmux', 'select-layout', '-t', f'{name}:0', 'tiled'])
        subprocess.run(['tmux', 'send-keys', '-t', f'{name}:0.0', 'claude', 'C-m'])
        subprocess.run(['tmux', 'send-keys', '-t', f'{name}:0.1', 'ranger', 'C-m'])

    def list_project_dirs(self) -> List[str]:
        return list_project_dirs()

    def session_exists(self, name: str) -> bool:
        out = self.run('has-session', '-t', name)
        return out == ''

    def start_missing_sessions(self):
        existing = {s['name'] for s in self.sessions}
        for path in self.list_project_dirs():
            name = os.path.basename(path)
            if name in existing:
                continue
            self.create_four_pane_session(name, path)

    def open_directory_in_view(self):
        self.display_header("OPEN DIRECTORY IN TMUX VIEW")
        dirs = self.list_project_dirs()
        sel = None
        try:
            import shutil, subprocess
            if shutil.which('fzf'):
                proc = subprocess.run(['fzf','--height','90%','--reverse','--prompt','Project: '], input='\n'.join(dirs), text=True, capture_output=True)
                sel = proc.stdout.strip() or None
        except Exception:
            sel = None
        if not sel:
            for i,d in enumerate(dirs): print(f"{i+1:2d}. {d}")
            print("\nDirectory # (or 'q'): ", end='')
            ch=input().strip()
            if ch.lower()=='q': return
            try:
                idx=int(ch)-1
                if 0<=idx<len(dirs): sel=dirs[idx]
                else: return
            except ValueError: return
        path=sel
        name=os.path.basename(path)
        if any(s['name']==name for s in self.sessions):
            print(f"{Colors.YELLOW}Session already exists: {name}{Colors.RESET}"); import time; time.sleep(1.5); return
        self.create_four_pane_session(name, path)
        print(f"{Colors.GREEN}Opened {name} with 4-pane view (Claude, Ranger, 2 terminals).{Colors.RESET}"); import time; time.sleep(1.5)

    def main_menu(self):
        while True:
            self.refresh()
            self.display_header("TMUX MANAGER")
            total_apps = {}
            for session in self.sessions:
                summary = self.get_session_app_summary(session['name'])
                for app_type, count in summary['app_counts'].items():
                    total_apps[app_type] = total_apps.get(app_type, 0) + count
            print(f"Session: {Colors.GREEN}{self.current_session}{Colors.RESET} | Total: {len(self.sessions)}")
            if total_apps:
                app_summary = []
                if total_apps.get('claude', 0) > 0:
                    app_summary.append(f"{Colors.CYAN}{total_apps['claude']} claude{Colors.RESET}")
                if total_apps.get('python', 0) > 0:
                    app_summary.append(f"{Colors.YELLOW}{total_apps['python']} python{Colors.RESET}")
                if total_apps.get('node', 0) > 0:
                    app_summary.append(f"{Colors.GREEN}{total_apps['node']} node{Colors.RESET}")
                if total_apps.get('editor', 0) > 0:
                    app_summary.append(f"{Colors.MAGENTA}{total_apps['editor']} editor{Colors.RESET}")
                if total_apps.get('browser', 0) > 0:
                    app_summary.append(f"{Colors.BLUE}{total_apps['browser']} browser{Colors.RESET}")
                if total_apps.get('shell', 0) > 0:
                    app_summary.append(f"{Colors.WHITE}{total_apps['shell']} shell{Colors.RESET}")
                if app_summary:
                    print(f"Apps: {' | '.join(app_summary)}")
            print()
            self.display_session_list()
            print(f"\n{Colors.YELLOW}Commands:{Colors.RESET}")
            print("  1) Details  2) Close  3) Switch  4) Tips  5) Start Missing  6) Open Dir  7) Exit")
            print(f"\nChoice: ", end='')
            choice = input().strip()
            if choice == '1':
                self.show_session_details_interactive()
            elif choice == '2':
                self.interactive_close_session()
            elif choice == '3':
                self.switch_to_session()
            elif choice == '4':
                self.show_quick_tips()
            elif choice == '5':
                self.start_missing_sessions()
                print(f"{Colors.GREEN}Started missing project sessions with 4-pane layout.{Colors.RESET}")
                time.sleep(1.5)
            elif choice == '6':
                self.open_directory_in_view()
            elif choice == '7':
                print(f"\n{Colors.GREEN}Sessions remain active.{Colors.RESET}")
                break
            else:
                continue
    
    
    def show_session_details_interactive(self):
        """Interactive session detail viewer"""
        self.display_header("SESSION DETAILS")
        self.display_session_list()
        
        print(f"\nSession # (or 'q'): ", end='')
        choice = input().strip()
        
        if choice.lower() == 'q':
            return
        
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(self.sessions):
                return
            
            session = self.sessions[idx]
            print(f"\n{Colors.YELLOW}{session['name']}{Colors.RESET}")
            print(f"Status: {'Current' if session['is_current'] else 'Attached' if session['attached'] else 'Detached'}")
            
            windows = self.get_windows(session['name'])
            for window in windows:
                print(f"\n  Window: {window['name']} ({window['panes']} panes)")
                panes = self.get_panes(session['name'], window['id'].replace('@', ''))
                for pane in panes:
                    print(f"    - {pane['title']} [{pane['command']}]")
            
            input(f"\nPress Enter...")
            
        except ValueError:
            return
    
    
    def show_quick_tips(self):
        """Show quick tmux tips"""
        self.display_header("QUICK TIPS")
        
        print(f"{Colors.YELLOW}Key Bindings:{Colors.RESET}")
        print("  Ctrl-b d     - Detach from session")
        print("  Ctrl-b c     - New window")
        print("  Ctrl-b n/p   - Next/Previous window")
        print("  Ctrl-b %     - Split vertical")
        print('  Ctrl-b "     - Split horizontal')
        print("  Ctrl-b arrow - Navigate panes")
        
        print(f"\n{Colors.YELLOW}Commands:{Colors.RESET}")
        print("  tmux ls             - List sessions")
        print("  tmux attach -t name - Attach to session")
        print("  tmux new -s name    - Create session")
        
        input(f"\nPress Enter...")

def main():
    """Main entry point"""
    manager = TmuxManager()
    
    if not os.environ.get('TMUX'):
        print(f"{Colors.YELLOW}Note: You're not currently in a tmux session.{Colors.RESET}")
        print("Some features may be limited.\n")
    
    try:
        manager.main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GREEN}Interrupted. Your tmux sessions remain active.{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
