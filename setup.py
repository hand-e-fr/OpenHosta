from setuptools import setup, find_packages

setup(
    name='OpenHosta',
    version='0.1.0',
    author='Léandre Ramos, Merlin Devillard, William Jolivet, Emmanuel Batt',
    description='Open-Source programming project for natural language programming with AI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hand-e-fr/OpenHosta-dev/tree/main',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.8',
        'License :: Open-Source',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Natural Language :: French',
        'Topic :: Software Development :: Code Generators'
    ],
    python_requires='>=3.8',
)