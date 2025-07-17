from setuptools import setup, find_packages

setup(
    name='vps_manager',
    version='0.1.0',
    packages=find_packages(),
    description='A simple VPS management tool.',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/vps_manager',
    install_requires=[
        'fastapi',
        'uvicorn',
        'paramiko',
        'python-dotenv',
    ],
)
