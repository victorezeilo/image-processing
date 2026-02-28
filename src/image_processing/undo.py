from pathlib import Path

try:
    from . import utilities
except ImportError:
    import utilities


def add_undo_arguments(subparsers, parent):
    p = subparsers.add_parser(
        "undo",
        help="Undo the last overwrite of a file (restores previous version from .history)",
        parents=[parent],
    )
    p.add_argument("-s", "--source", type=utilities.valid_file, required=True, help="File to undo (restore previous version)")


def undo_last(args):
    target = Path(args.source).resolve()
    history = utilities._load_history()

    key = str(target)
    if key not in history or not history[key]:
        utilities.error(f"No undo history found for: {target}")

    last_backup = Path(history[key].pop()).resolve()

    if not last_backup.exists():
        utilities.error(f"Backup missing: {last_backup}")

    # restore backup over the target
    import shutil
    shutil.copy2(last_backup, target)

    # save updated history
    if not history[key]:
        del history[key]
    utilities._save_history(history)

    print(f"\033[32mUndo successful. Restored: {target}\033[0m")