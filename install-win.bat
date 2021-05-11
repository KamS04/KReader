@echo off

:DOES_PYTHON_EXIST
python -V | find /v "Python 3">NUL 2>NUL && (goto :PYTHON_DOES_NOT_EXIST)
python -V | find "Python 3">NUL 2>NUL && (goto :PYTHON_DOES_EXIST)
goto :EOF

:PYTHON_DOES_NOT_EXIST
echo Python 3 does not exist
echo Python 3 can be installed from https://www.python.org/downloads/
echo If you have already installed python, maybe you have not added it to Path
goto :EOF

:PYTHON_DOES_EXIST
echo Python exists
goto :CHECK_PIP_EXISTS

:CHECK_PIP_EXISTS
python -m pip --version | find /v "pip">NUL 2>NUL && (goto :PIP_DOES_NOT_EXIST)
python -m pip --version | find "pip">NUL 2>NUL && (goto :PIP_EXISTS)
goto :EOF

:PIP_DOES_NOT_EXIST
echo Pip does not exist
echo Download pip from https://bootstrap.pypa.io/get-pip.py
echo Then run the file with python
goto :EOF

:PIP_EXISTS
echo Pip exists
if exist venv\NUL (
    goto :RUN_INSTALL
) else (
    goto :CREATE_VIRTUAL_ENV
)
goto :EOF

:CREATE_VIRTUAL_ENV
echo Creating Virtual Environment
python -m pip install virtualenv
python -m virtualenv venv
goto :RUN_INSTALL
goto :EOF

:RUN_INSTALL
call "./venv/scripts/activate.bat"
python -m pip install -r dist/requirements.txt
python -m pip install kivy kivymd
echo Installed
goto :EOF
