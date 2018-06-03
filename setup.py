from setuptools import setup
setup(name='ucdev',
      version='0.0.2',
      description='Library to access various I2C/SPI/GPIO-accessible chips over Cypress CY7C65211/3/5 USB-to-UART/I2C/SPI/GPIO bridge.',
      url='https://github.com/tai/python-ucdev/',
      author='Taisuke Yamada',
      author_email='tai@remove-if-not-spam.rakugaki.org',
      license='MIT',
      packages=['ucdev'],
      install_requires=[
          'bitstring',
          'cffi',
          'IPython',
      ]
)
