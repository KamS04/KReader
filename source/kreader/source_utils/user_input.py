from plyer import filechooser

async def choose_file(*file_types, title='Select file', initial_dir='~/'):
    return filechooser.open_file(title=title, path=initial_dir, filters=file_types)

async def choose_dir(title='Select directory', initial_dir='~/'):
    return filechooser.choose_dir(path=initial_dir, title=title)

if __name__ == '__main__':
    choose_file()