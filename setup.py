import setuptools
import scpper

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

with open('README.md', encoding="utf8") as f:
    readme = f.read()

setuptools.setup(
    name='scpper',
    version=scpper.__version__,
    description='Python wrapper for ScpperDB API.',
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/skippy-dev/scpper/',
    author='MrNereof',
    author_email='mrnereof@gmail.com',
    python_requires='>=3.9',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'Programming Language :: Python :: 3.9'],
    keywords=['scp', 'scpper', 'api'],
    packages=['scpper'],
    install_requires=requirements,
)
