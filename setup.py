from setuptools import setup

setup(name='cbpi4-sensor-dependant-actor',
      version='0.0.1',
      description='CraftBeerPi Plugin',
      author='Kenny',
      author_email='',
      url='https://github.com/Kenny4487/cbpi4-sensor-dependant-actor/',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-sensor-dependant-actor': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-sensor-dependant-actor'],
     )