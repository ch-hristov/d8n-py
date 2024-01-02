from setuptools import setup, find_packages

setup(
    name='d8n',
    version='0.2.6',
    author='Christo',
    author_email='christochristov@duck.com',
    description='d8n API python library',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)