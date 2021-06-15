import setuptools

with open('README.md', 'r') as fh:
	long_description = fh.read()

setuptools.setup(
	name='fuzzytools',
	version='0.2',
	description='Library with basic and general python methods',
	url='https://github.com/opimentel-github/fuzzy-tools',
	python_requires='>=3.7',
	install_requires=[
		'joblib',
		'numpy',
		'matplotlib',
		'scikit-learn',
		'scipy',
		'termcolor',
		'tqdm',
		'pandas',
		'nested-dict',
		'numba',
		'Pillow',
		'imageio',
		'imageio-ffmpeg',
		],
	keywords='experimental',
	author='Oscar Pimentel Fuentes',
	author_email='oscarlo.pimentel@gmail.com',
	#include_package_data=True,
	packages=setuptools.find_packages(),
	long_description=long_description,
	long_description_content_type='text/markdown',
	license='MIT licence',
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		],
)
