from setuptools import setup

setup(name='mwdump',
      version='0.3',
      description='MediaWiki dump file reader',
      url='https://github.com/cllu/mwdump',
      author='Chunliang Lyu',
      author_email='hi@chunlianglyu.com',
      license='MIT',
      packages=['mwdump'],
      install_requires=['lxml'],
      zip_safe=False
)
