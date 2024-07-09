from setuptools import setup, find_packages

setup(
    name='OpenHosta',
    version='1.0',
    author='Léandre Ramos, Merlin Devillard, William Jolivet, Emmanuel Batt',
    license='MIT License',
    description='Open-Source programming project for natural language programming with AI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hand-e-fr/OpenHosta-dev/tree/main',
    packages=find_packages(),
    license_file=('LICENSE',),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Natural Language :: French',
        'Topic :: Software Development :: Code Generators'
    ],
    python_requires='>=3.8',
)