from setuptools import setup

with open('requirements.txt') as file:
    requirements = [r.rstrip('\n') for r in file]

setup(
    name='nagios-plugins-stacktask',
    version='0.1',
    author='Catalyst Cloud Team',
    author_email='cloud@catalyst.net.nz',
    url='http://www.catalyst.net.nz',
    packages=['nagios_plugins_stacktask'],
    entry_points={
        'console_scripts': [
            'check_stacktask_notifications=nagios_plugins_stacktask:main'
        ],
    },
    install_requires=requirements,
    include_package_data=True
)
