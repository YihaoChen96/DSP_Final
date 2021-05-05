from setuptools import setup, find_packages

setup(
    name='pySynth', 
    version='0.1', 
    packages=find_packages(),
    install_requires = ["numpy", "scipy", "simpleaudio", "pretty-midi", "SoundFile"]
    )