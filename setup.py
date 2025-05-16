from setuptools import setup

APP = ['popamole.py']
DATA_FILES = [
    ('Media', [
        'Media/water-squirt.png',
        'Media/PopAMole-WaterShot.mp3',
        'Media/PopAMole-MoleHit.mp3',
        'Media/PopAMole.mp3',
        'Media/mole.png',
        'Media/mole.ico'
    ])
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
    'iconfile': 'Media/mole.ico',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)