from setuptools import setup

APP = ['Gruppengenerator.py']
DATA_FILES = ['resources/participants.csv']
OPTIONS = {
    'argv_emulation': True,
    'includes': ['customtkinter'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
