import sys
from setuptools import setup, find_packages

sys.dont_write_bytecode = True

setup(
    name="chatapp",
    version="0.0.1",
    description='Simple Chat Application.',
    long_description='',
    author='Mundia Mwala',
    author_email='mundiamwala@gmail.com',
    url='https://mundia.me',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "chatapp=chatapp.cli:run",
        ],
    },
    install_requires=[
        "Flask==2.0.1",
        "gunicorn==20.0.4",
        "gevent==21.1.2",
        "python-dotenv==0.17.0",
        "bcrypt==3.2.0",
        "tornado==6.1",
        "twilio==7.4.0",
    ],
    license="MIT",
    python_requires=">=3.7",
)

