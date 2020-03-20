from distutils.core import setup

setup(
    name='awesomedoc',
    packages=['awesomedoc'],
    version='1.0.alpha',
    license='MIT',
    description='Generate simple markdown from python scripts',
    author='Tom Naumann',
    author_email='tom.naumann.95@gmail.com',
    url="https://github.com/tomnaumann/pydoc",
    keywords=['markdown', 'awesomedoc', 'documentation'],
    entry_points={
        'console_scripts': [
            'awesomedoc = awesomedoc.main:main',
        ],
    },
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
