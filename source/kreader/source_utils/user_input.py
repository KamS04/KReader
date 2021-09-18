KIVY_MODE = False
try:
    import tkinter
    from tkinter.filedialog import askopenfilename, askdirectory
except ModuleNotFoundError:
    KIVY_MODE = True

def create_withdrawn_tkinter():
    root = tkinter.Tk()
    root.withdraw()
    return root

def choose_file(*file_types, title='Select file', initial_dir='~/'):
    if not KIVY_MODE:
        root = tkinter.Tk()
        root.withdraw()
        path = askopenfilename(title=title, filetypes=file_types, initialdir=initial_dir)
        root.destroy()

        return path

    return None

def choose_dir(title='Select directory', initial_dir='~/'):
    if not KIVY_MODE:
        root = create_withdrawn_tkinter()
        path = askdirectory(initialdir=initial_dir, title=title)
        root.destroy()

        return path

if __name__ == '__main__':
    choose_file()