from setuptools import setup
from winspeech import __doc__ as long_description

setup(
    name='winspeech',
    version='1.0.1',
    py_modules=['winspeech'],
    description='Speech recognition and synthesis module for Windows - Python 2 and 3.',
    long_description=long_description,
    url='https://github.com/areebbeigh/winspeech',
    author='Areeb Beigh',
    author_email='areebbeigh@gmail.com',
    license='Apache License 2.0',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Home Automation',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='speech recognition synthesis tts text-to-speech windows SAPI',
    install_requires=["pywin32"]
)
