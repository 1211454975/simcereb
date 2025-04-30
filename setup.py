from setuptools import setup, find_packages  
  
setup(  
    name="simcereb",  
    version="0.1.0",  
    description="Educational platform for humanoid robot cerebellum system simulation",  
    author="SimCereb Team",  
    author_email="info@simcereb.org",  
    packages=find_packages(),  
    install_requires=[  
        "pybullet>=3.2.0",  
        "numpy>=1.20.0",  
        "matplotlib>=3.4.0",  
        "PyYAML>=6.0",  
        "PyQt5>=5.15.0",  
    ],  
    classifiers=[  
        "Development Status :: 3 - Alpha",  
        "Intended Audience :: Education",  
        "License :: OSI Approved :: MIT License",  
        "Programming Language :: Python :: 3",  
        "Topic :: Scientific/Engineering :: Artificial Intelligence",  
        "Topic :: Education",  
    ],  
    include_package_data=True,  
    package_data={  
        "simcereb": ["configs/*.yaml", "models/*.urdf"],  
    },  
)  