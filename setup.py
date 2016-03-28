from distutils.core import setup

setup(
    name='ODA',
    version='1.0',
    description='OrderBook utilities',
    author='ANFI',
    author_email='grupoanfi@gmail.com',
    packages=['ODA', 'ODA.test'],
    license='OSI Approved',
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Legal Industry',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business :: Financial',
    ]
)

