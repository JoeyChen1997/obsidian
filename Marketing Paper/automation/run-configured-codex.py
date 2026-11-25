"""Launch the approved Paperlist model route without copying credentials."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from urllib.parse import urlsplit


def codex_arguments(config):
    provider = config['model_provider']
    if not re.fullmatch(r'[A-Za-z0-9_-]+', provider):
        raise ValueError('Unexpected provider identifier')
    base = config['model_providers'][provider]['base_url']
    url = urlsplit(base)
    if (url.scheme != 'https' or url.hostname != 'api.site' or url.port not in (None, 443)
            or url.username or url.password or url.query or url.fragment):
        raise ValueError('Only the approved HTTPS model host is allowed')
    args = ['-a', 'never', 'exec', '--ephemeral', '--skip-git-repo-check',
            '-s', 'workspace-write', '--disable', 'hooks', '--disable', 'plugins',
            '-c', 'windows.sandbox="unelevated"',
            '-c', 'sandbox_workspace_write.network_access=false',
            '-c', 'web_search="disabled"', '-c', f'model_provider={json.dumps(provider)}',
            '-c', f'model_providers.{provider}.base_url={json.dumps(base)}',
            '--color', 'never', '--json']
    for name in config.get('mcp_servers', {}):
        if not re.fullmatch(r'[A-Za-z0-9_-]+', name):
            raise ValueError('Unexpected MCP identifier')
        args.extend(['-c', f'mcp_servers.{name}.enabled=false'])
    return args


def main():
    project = Path(__file__).resolve().parents[1]
    try:
        # These layers can add project-specific hooks, MCPs, or provider settings.
        # Refuse to run rather than silently trust a newly introduced config layer.
        config_home = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex').resolve()
        if any(d.resolve() != config_home and (d / 'config.toml').is_file()
               for d in (p / '.codex' for p in (project, *project.parents))):
            raise ValueError('Additional project config layer')
        config = tomllib.loads((config_home / 'config.toml').read_text(encoding='utf-8-sig'))
        args = codex_arguments(config)
        executable = Path(os.environ['APPDATA']) / (
            'npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/'
            'vendor/x86_64-pc-windows-msvc/bin/codex.exe')
        prompt = Path(__file__).with_name('reading-prompt.md').read_bytes()
        if not executable.is_file():
            raise FileNotFoundError('Codex executable')
    except (KeyError, TypeError, ValueError, OSError):
        return 6

    # The CLI loads the existing user config itself. No authorization value is
    # copied to arguments, a new file, stdout or the scheduled task definition.
    env = os.environ.copy()
    env.pop('OPENAI_BASE_URL', None)
    env.pop('OPENAI_API_BASE', None)
    try:
        result = subprocess.run([str(executable), *args, '-C', str(project), '-'],
                                cwd=project, env=env, input=prompt,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                timeout=21 * 60)
    except subprocess.TimeoutExpired:
        return 7
    except OSError:
        return 8
    events = set()
    commands = command_errors = patches = 0
    clues = set()
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                continue
            if event.get('type') in {'turn.completed', 'turn.failed'}:
                events.add(event['type'])
            if event.get('type') == 'item.completed':
                item = event.get('item', {})
                if item.get('type') == 'command_execution':
                    commands += 1
                    command_errors += item.get('exit_code') != 0
                    if item.get('exit_code') != 0:
                        command = str(item.get('command', '')).lower()
                        for label, marker in {'pdf': 'pdftotext', 'coverage': 'reading_coverage.py',
                                              'skill': 'skill.md', 'graph': 'research_graph.json',
                                              'queue': '逐篇核读', 'directory': 'get-childitem'}.items():
                            if marker in command:
                                clues.add(label)
                if item.get('type') == 'file_change':
                    patches += 1
                details = str(item.get('aggregated_output', '')) + str(item.get('text', ''))
                for label, pattern in {
                    'sandbox': r'sandbox failed|CreateProcessAsUser|restricted token',
                    'access': r'access is denied|permission denied|拒绝访问|权限不足',
                    'missing': r'cannot find|not recognized|not found|找不到|不存在',
                    'tools': r'no (?:shell|tools)|没有.{0,12}工具|无法.{0,12}(?:工具|运行命令)',
                    'provider': r'401 Unauthorized|403 Forbidden|429 Too Many Requests',
                }.items():
                    if re.search(pattern, details, re.IGNORECASE):
                        clues.add(label)
        except (ValueError, UnicodeError):
            continue
    print(f'cli_exit={result.returncode} completed={int("turn.completed" in events)} '
          f'commands={commands} command_errors={command_errors} patches={patches} '
          f'clues={"+".join(sorted(clues)) or "none"}')
    return 0 if result.returncode == 0 and 'turn.completed' in events and 'turn.failed' not in events else 9


if __name__ == '__main__':
    sys.exit(main())
