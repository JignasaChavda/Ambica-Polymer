from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ambica_polymer/__init__.py
from ambica_polymer import __version__ as version

setup(
	name="ambica_polymer",
	version=version,
	description="App for Ambica Polymer Customization",
	author="Jignasa Chavda",
	author_email="jignasha@sanskartechnolab.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
