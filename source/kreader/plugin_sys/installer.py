import os
import zipfile


def install_plugin(destination_path: str, plugin_path: str):
    plugin_name = os.path.basename(plugin_path) # assuming .zip file
    plugin_dirname = plugin_name.split('.')[0]
    plugin_dir = tmp_plugin_dir = os.path.join(destination_path, plugin_dirname)

    idx = 0
    while True:
        if os.path.exists(tmp_plugin_dir):
            idx += 1
            tmp_plugin_dir += str(idx)
        else:
            break

    plugin_dir = tmp_plugin_dir

    os.makedirs(plugin_dir)

    plugin_zip = zipfile.ZipFile(plugin_path)
    plugin_zip.extractall(plugin_dir)
    module_name = os.path.basename(plugin_dir)
    
    return module_name, plugin_dir
