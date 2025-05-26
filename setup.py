from setuptools import setup, find_packages

setup(
    name='personal-assistant',
    version='0.1.0',
    description='A personal assistant application that manages notes, calendars, emails, and more.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        # List your project dependencies here
        'requests',
        'streamlit',
        'faiss-cpu',  # or 'faiss-gpu' if you are using GPU
        'openai',     # if using OpenAI API
        # Add other dependencies as needed
    ],
    entry_points={
        'console_scripts': [
            'personal-assistant=main:main',  # Assuming main function is defined in main.py
        ],
    },
)