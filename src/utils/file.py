import os
import shutil


def delete_dir_if_exists(path):
    # Skip if dir does not exist
    if not os.path.exists(path):
        return

    # Ensure the tree is writable
    os.chmod(path, 0o7777)
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        print(item_path)
        if os.path.isdir(item_path):
            os.chmod(item_path, 0o7777)
            delete_dir_if_exists(item_path)
        if os.path.isfile(item_path):
            os.chmod(item_path, 0o7777)

    # Delete
    shutil.rmtree(path)
