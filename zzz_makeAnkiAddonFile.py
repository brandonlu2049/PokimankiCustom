import os
import zipfile
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .custom_py.popup.popup_config import NEW_FEATURE
    from .custom_py.popup.change_log import OLD_CHANGE_LOG


def create_ankiaddon():
    # Use the script's directory, not the current working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    today = datetime.today().strftime('%Y%m%d%H%M')

    zip_name = f'addon_{today}.zip'

    # exclude_dirs = ['__pycache__', 'bundle03', '.vscode']
    exclude_dirs = ['__pycache__', 'bundle03', 'user_files', '.vscode', '.git']
    exclude_exts = ['.ankiaddon']
    exclude_files = ['meta.json', zip_name, "template_00.md"]

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(current_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file not in exclude_files and os.path.splitext(file)[1] not in exclude_exts:
                    zipf.write(os.path.join(root, file),
                                os.path.relpath(os.path.join(root, file),
                                                current_dir))
    os.rename(zip_name, f'Pokemanki_{today}.ankiaddon')

print("creating add on file")
create_ankiaddon()
print("finished making add on file")