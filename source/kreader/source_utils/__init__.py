from ..utils.preferences import PreferencesManager

def register(plugin):
    raise Exception(f'{plugin} is accessing Register before/after plugins are loaded')

def get_prefs() -> PreferencesManager:
    raise Exception('No preference manager setup yet')

def get_install_directory() -> str:
    raise Exception('No Install directory specified')
