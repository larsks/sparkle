from setuptools import setup, find_packages

setup(
    name='sparkle',
    version='0.1',
    author='Lars Kellogg-Stedman',
    author_email='lars@oddbit.com',
    url='https://github.com/larsks/sparkle',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sparkle = sparkle.main:cli',
        ],
        'sparkle.cmd': [
            'broker = sparkle.cmd.broker:broker',
            'button = sparkle.cmd.button:button',
            'monitor = sparkle.cmd.monitor:monitor',
        ]
    }
)
