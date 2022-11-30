from setuptools import setup, find_packages

with open('Readme.md') as f:
    txt = f.read()

setup(name='kbib',
    version='0.1.5',
    description='A command line tool to get bibtex information from DOIs and PDFs',
    long_description=txt,
    long_description_content_type='text/markdown',
    author='Koushik Naskar',
    author_email='koushik.naskar9@gmail.com',
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console', 
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Shells'
    ],
    keywords='bibtex references doi crossref',
    project_urls={'Source Code': 'https://github.com/Koushikphy/kbib'},
    zip_safe=True,
    python_requires='>=3.6',
    packages=find_packages(),
    install_requires=[
        'bibtexparser>=1.4.0',
        'rich>=12.6.0',
        'requests_cache'
    ],
    extras_require = {
        'pdf': ['pdf2doi']
    },
    entry_points={
        'console_scripts': [
            'kbib = kbib.parseRefs:main',
        ],
    }
)
