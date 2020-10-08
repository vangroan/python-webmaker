"""
Static site generator
"""
from setuptools import find_packages, setup


def load_requirements():
    with open('requirements.txt', 'r') as fp:
        return [dependency.strip() for dependency in fp if dependency.strip()]


setup(
    name='webmaker',
    version='0.1.0',
    url='https://gitlab.com/vangroan/webmaker',
    license='MIT',
    author='Willem Victor',
    author_email='wimpievictor@gmail.com',
    description='Static site generator',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=load_requirements(),
    entry_points={
        'console_scripts': [
            'web-maker = web_maker.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        # 'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
