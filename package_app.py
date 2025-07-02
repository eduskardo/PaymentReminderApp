import os
import zipfile

EXCLUDES = {'.git', '__pycache__'}


def should_include(path):
    parts = path.split(os.sep)
    for p in parts:
        if p in EXCLUDES:
            return False
    return True


def package(zip_name='PaymentReminderApp.zip'):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('.'):            
            dirs[:] = [d for d in dirs if should_include(os.path.join(root, d))]
            for f in files:
                file_path = os.path.join(root, f)
                if not should_include(file_path):
                    continue
                zf.write(file_path, os.path.relpath(file_path, '.'))
    print(f"Created {zip_name}")


if __name__ == '__main__':
    package()
