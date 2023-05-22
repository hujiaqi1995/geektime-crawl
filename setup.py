from setuptools import setup, find_packages


setup(
    name='greekcrawl',
    version='0.0.1',
    description='Crawl greek time articles',
    url='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='crawl',
    packages=find_packages(),
    install_requires=[
        'requests==2.31.0',
        'pdfkit==0.6.1'
    ],

    entry_points={
        'console_scripts': [
            'greek-time-crawler=greekcrawl.crawl:main'
        ],
    },
)
