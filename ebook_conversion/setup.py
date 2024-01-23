from setuptools import setup, find_packages

setup(
    name='Ebook conversion to Text for Machine Learning',
    version='1.0.0',
    packages=find_packages(),
    description='Converts common ebook file types to text for machine learning',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ashlynn Antrobus',
    author_email='ashlynn@prosepal.io',
    url='https://github.com/ashrobertsdragon/Ebook-conversion-to-Text-for-Machine-Learning',
    install_requires=[
        "beautifulsoup4>=4.12.3",
        "certifi>=2023.11.17",
        "charset-normalizer>=2,<4",
        "EbookLib==0.18",
        "idna>2.5.0,<4",
        "lxml>3.1.0",
        "python-docx=>1.1.0",
        "python-dotenv>=1.0.1",
        "pillow>=10.2.0",
        "requests==2.31.0",
        "six==1.16.0",
        "soupsieve>1.2",
        "style==1.1.0",
        "typing-extensions<3.10",
        "update==0.0.1",
        "urllib3>=1.21.1,<3"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
