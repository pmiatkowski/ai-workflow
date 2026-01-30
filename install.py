#!/usr/bin/env python3
"""
AI Workflow Installer
Customizes the workflow folder name from .ai-workflow to user's choice.

Usage:
  python install.py              # Interactive mode
  python install.py <folder>     # Non-interactive mode
  python install.py --help       # Show help
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from glob import glob


def main():
    # Handle command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print(__doc__)
            return
        folder_name = sys.argv[1]
        interactive = False
    else:
        interactive = True
        folder_name = None

    print("=" * 60)
    print("AI Workflow Installer")
    print("=" * 60)
    print()

    # 1. Check if already installed
    if Path('.aiconfig').exists():
        print("[ERROR] Already installed. Remove .aiconfig to reinstall.")
        sys.exit(1)

    # 2. Validate prerequisites
    if not Path('.ai-workflow').exists():
        print("[ERROR] .ai-workflow folder not found")
        print("        Make sure you're running this from the project root.")
        sys.exit(1)

    # 3. Get user input
    if interactive:
        print("This installer will customize your AI workflow folder name.")
        print()
        folder_name = input("Workflow folder name [.ai]: ").strip() or ".ai"
    else:
        print(f"Installing with folder name: {folder_name}")
        print()

    # 4. Validate input
    try:
        validate_folder_name(folder_name)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # 5. Check for conflicts
    if Path(folder_name).exists():
        print(f"[ERROR] {folder_name} already exists")
        sys.exit(1)

    # 6. Ask about installing commands
    if interactive:
        print()
        install_commands_choice = input("Install commands to .claude/commands/? (y/n): ").strip().lower()
        install_commands_flag = install_commands_choice in ['y', 'yes']
    else:
        install_commands_flag = False

    # 7. Ask about PR configuration
    if interactive:
        print()
        print("Pull Request Configuration:")
        pr_tool = input("  PR tool (gh/az) [gh]: ").strip().lower() or "gh"
        if pr_tool not in ['gh', 'az']:
            print(f"  [WARNING] Unknown tool '{pr_tool}', defaulting to 'gh'")
            pr_tool = 'gh'
        
        pr_convention = input("  Commit convention (conventional/ticket-prefix) [conventional]: ").strip().lower() or "conventional"
        if pr_convention not in ['conventional', 'ticket-prefix']:
            print(f"  [WARNING] Unknown convention '{pr_convention}', defaulting to 'conventional'")
            pr_convention = 'conventional'
        
        pr_base_branch = input("  Default base branch [main]: ").strip() or "main"
    else:
        pr_tool = "gh"
        pr_convention = "conventional"
        pr_base_branch = "main"

    # 8. Preview changes
    print()
    print_preview(folder_name, install_commands_flag, pr_tool, pr_convention, pr_base_branch)

    # 9. Confirm
    print()
    if interactive and not confirm("Proceed with installation?"):
        print("Installation cancelled.")
        return
    elif not interactive:
        print("Proceeding with installation (non-interactive mode)...")
        print()

    # 10. Execute
    print()
    print("Installing...")
    print()
    try:
        rename_workflow_folder(folder_name)
        update_file_contents(folder_name)
        update_pr_config(folder_name, pr_tool, pr_convention, pr_base_branch)
        update_vscode_settings(folder_name)
        create_config_marker(folder_name)
        if install_commands_flag:
            print()
            install_commands(folder_name)
        print()
        print("=" * 60)
        print(f"[SUCCESS] Installation complete! Workflow folder: {folder_name}")
        print("=" * 60)
    except Exception as e:
        print(f"[ERROR] Installation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def validate_folder_name(name):
    """Validate folder name"""
    if not name:
        raise ValueError("Folder name cannot be empty")
    if ' ' in name:
        raise ValueError("Folder name cannot contain spaces")
    if not name.startswith('.'):
        print(f"[WARNING] {name} doesn't start with '.' - continuing anyway")
    # Check for invalid path characters (Windows + Unix)
    invalid_chars = '<>:"|?*'
    if any(c in name for c in invalid_chars):
        raise ValueError(f"Folder name contains invalid characters: {invalid_chars}")


def rename_workflow_folder(new_name):
    """Rename .ai-workflow to custom name"""
    os.rename('.ai-workflow', new_name)
    print(f"[OK] Renamed .ai-workflow -> {new_name}")


def update_file_contents(new_folder_name):
    """Replace .ai-workflow references in all files"""
    # Note: After renaming, files are now in the new folder
    # Note: Prompt files use ai.*.prompt.md naming convention
    files_to_update = [
        f'{new_folder_name}/config.yml',
        f'{new_folder_name}/scripts/*.py',
        f'{new_folder_name}/prompts/*.prompt.md',  # Matches both ai.*.prompt.md and any legacy *.prompt.md
        '.vscode/settings.json',
        'CLAUDE.md'
    ]

    total_replacements = 0
    files_updated = 0

    for file_pattern in files_to_update:
        for file_path in glob_files(file_pattern):
            # Only replace .ai-workflow folder references, not command prefixes
            # Command prefixes (e.g., /ai.add) should remain unchanged
            # This ensures idempotency - running install multiple times is safe
            replacements = replace_in_file(file_path, '.ai-workflow', new_folder_name)
            if replacements > 0:
                total_replacements += replacements
                files_updated += 1

    print(f"[OK] Updated {total_replacements} references across {files_updated} files")


def update_vscode_settings(folder_name):
    """Update VSCode settings.json"""
    settings_path = Path('.vscode/settings.json')
    if settings_path.exists():
        content = settings_path.read_text(encoding='utf-8')
        updated_content = content.replace('.ai-workflow/prompts', f'{folder_name}/prompts')
        settings_path.write_text(updated_content, encoding='utf-8')
        print("[OK] Updated VSCode settings")
    else:
        print("[WARNING] VSCode settings.json not found - skipping")


def create_config_marker(folder_name):
    """Create .aiconfig marker file"""
    config = f"""version: 1
installed: true
installation_date: {datetime.now().strftime('%Y-%m-%d')}
customizations:
  workflow_folder: {folder_name}
"""
    Path('.aiconfig').write_text(config, encoding='utf-8')
    print("[OK] Created .aiconfig marker")


def install_commands(workflow_folder):
    """Copy prompt files to .claude/commands/"""
    commands_dir = Path('.claude/commands')
    prompts_dir = Path(workflow_folder) / 'prompts'

    # Create .claude/commands directory if it doesn't exist
    commands_dir.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Created {commands_dir}")

    # Copy all .prompt.md files
    copied = 0
    for prompt_file in prompts_dir.glob('*.prompt.md'):
        dest = commands_dir / prompt_file.name
        dest.write_text(prompt_file.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"[OK]   Copied {prompt_file.name}")
        copied += 1

    return copied


# Helper functions

def glob_files(pattern):
    """Expand glob pattern to list of files"""
    if '*' in pattern:
        return [Path(p) for p in glob(pattern, recursive=True)]
    else:
        # Single file
        p = Path(pattern)
        return [p] if p.exists() else []


def replace_in_file(file_path, old_text, new_text):
    """Replace text in file, return count of replacements"""
    file_path = Path(file_path)
    if not file_path.exists():
        return 0

    try:
        content = file_path.read_text(encoding='utf-8')
        count = content.count(old_text)
        if count > 0:
            updated_content = content.replace(old_text, new_text)
            file_path.write_text(updated_content, encoding='utf-8')
        return count
    except Exception as e:
        print(f"[WARNING] Could not update {file_path}: {e}")
        return 0


def print_preview(folder_name, install_commands_flag=False, pr_tool="gh", pr_convention="conventional", pr_base_branch="main"):
    """Show what will be changed"""
    print("Preview of changes:")
    print("-" * 60)
    print(f"  Folder:    .ai-workflow -> {folder_name}")
    print(f"  Files:     100+ folder references will be updated")
    print(f"  Config:    config.yml, scripts/*.py, prompts/ai.*.prompt.md")
    print(f"  VSCode:    .vscode/settings.json")
    print(f"  Docs:      CLAUDE.md")
    print(f"  Marker:    .aiconfig will be created")
    if install_commands_flag:
        print(f"  Commands:  {folder_name}/prompts/ -> .claude/commands/ (yes)")
    else:
        print(f"  Commands:  {folder_name}/prompts/ -> .claude/commands/ (no)")
    print(f"  PR Tool:   {pr_tool} ({'GitHub CLI' if pr_tool == 'gh' else 'Azure DevOps CLI'})")
    print(f"  PR Style:  {pr_convention} commits, base branch: {pr_base_branch}")
    print(f"  Note:      Command prefixes (/ai.add, /ai.clarify) remain unchanged")
    print("-" * 60)


def update_pr_config(folder_name, pr_tool, pr_convention, pr_base_branch):
    """Update PR configuration in config.yml"""
    config_path = Path(folder_name) / "config.yml"
    if not config_path.exists():
        print("[WARNING] config.yml not found - skipping PR config update")
        return
    
    content = config_path.read_text(encoding='utf-8')
    
    # Update pull_request section values
    content = re.sub(
        r'(pull_request:\s*\n\s*tool:\s*)\S+',
        f'\\1{pr_tool}',
        content
    )
    content = re.sub(
        r'(commit_convention:\s*)\S+',
        f'\\1{pr_convention}',
        content
    )
    content = re.sub(
        r'(branch_format:\s*)\S+',
        f'\\1{pr_convention}',
        content
    )
    content = re.sub(
        r'(default_base_branch:\s*)\S+',
        f'\\1{pr_base_branch}',
        content
    )
    
    config_path.write_text(content, encoding='utf-8')
    print(f"[OK] Updated PR configuration in config.yml")


def confirm(message):
    """Get user yes/no confirmation"""
    while True:
        response = input(f"{message} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")


if __name__ == '__main__':
    main()
