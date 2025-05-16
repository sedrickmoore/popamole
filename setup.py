from setuptools import setup

APP = ['popamole.py']
DATA_FILES = [
    'water-squirt.png',
    'PopAMole-WaterShot.mp3',
    'PopAMole-MoleHit.mp3',
    'PopAMole.mp3',
    'mole.png'
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame', 'sqlite3', 're'],
    'includes': ['pygame', 'sqlite3', 're'],
    'plist': {
        'CFBundleName': 'Pop-A-Mole',
        'CFBundleShortVersionString': '1.0',
        'CFBundleIdentifier': 'com.sedrickmoore.popamole',
        'CFBundleVersion': '1.0'
    },
    'iconfile': 'mole.ico',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)