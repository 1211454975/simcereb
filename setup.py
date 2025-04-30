# setup.py  
"""  
Setup script for SimCereb  
"""  
  
from setuptools import setup, find_packages  
  
setup(  
    name="simcereb",  
    version="1.0.0",  
    description="Educational platform for humanoid robot cerebellum system simulation",  
    author="SimCereb Team",  
    author_email="info@simcereb.org",  
    packages=find_packages(),  
    include_package_data=True,  
    install_requires=[  
        "pybullet>=3.2.0",  
        "numpy>=1.20.0",  
        "matplotlib>=3.4.0",  
        "PyYAML>=6.0",  
        "PyQt5>=5.15.0",  
        "markdown>=3.3.0",  
        "psutil>=5.8.0",  
    ],  
    entry_points={  
        'console_scripts': [  
            'simcereb=simcereb.__main__:main',  
        ],  
    },  
    classifiers=[  
        "Development Status :: 4 - Beta",  
        "Intended Audience :: Education",  
        "License :: OSI Approved :: MIT License",  
        "Programming Language :: Python :: 3",  
        "Programming Language :: Python :: 3.7",  
        "Programming Language :: Python :: 3.8",  
        "Programming Language :: Python :: 3.9",  
        "Topic :: Education",  
        "Topic :: Scientific/Engineering :: Artificial Intelligence",  
        "Topic :: Scientific/Engineering :: Visualization",  
    ],  
    python_requires=">=3.7",  
)