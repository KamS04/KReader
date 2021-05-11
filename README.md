# KReader
Desktop Manga/Webtoon Reader

****
**Author**: Kam S

**Version**: 0.1.0

**Platform**: Python - Desktop ( Windows - MacOS - Linux )

****

Installation Instructions

1. Download and Install Python 3
    - You can download it here: [Python 3](https://www.python.org/downloads/)
    - For windows users, during installation there will be a box that says
        > Add Python 3.x to Path
      
      Make sure that is selected
    - During installation there may be checkbox for
        > tcl/tc and IDLE
    
      Make Sure it is selected
2. Install pip
    - Normally this comes with python, in your terminal/command prompt try 
        ```
        pip --version
        ```
     If this gives an error then download [this file](https://bootstrap.pypa.io/get-pip.py) and run it with python.
3. Download the repository and unzip it.
    - Click on the green *Code* button
5. Run the install script. 
    - For windows users, run ```install-win.bat``` (Either double click on the file or run it in a command prompt)
    - For MacOS or Linux users, run ```install-mac```  (Either double click on the file or run it in a terminal)
        - In the terminal run it with the following command
         ```
         bash install-mac
         ```
    - Linux uses must also install tkinter, this varies with distribution so you can do it yourselves
        -  For distribution based on Debian the following command will work
        ```
        sudo apt-get install pyt
        ```
        - For distributions based on Fedora the following command will work
        ```
        sudo dnf install python3-tkinter
        ```
6. Run the KReader script
    - For windows users, run ```KReader-win.bat```
    - For MacOS or Linux, run ```KReader-mac```
        - In the terminal run it with the following command
        ```
        bash KReader-mac
        ```

****
Once at the home screen, click on ***MangaDex*** then either use the search box to search for manga, or use the select button to put in the url for a manga.
The app is a bit slow, but it's only meant to be a temporary fix until mangadex comes back.

The ***CBZ*** source can open images inside ```.zip``` or ```.cbz``` files.
