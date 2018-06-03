from setuptools import setup
setup(name='ucdev',
      version='0.0.2',
      description='Library to access Nordic nRF24L01 wireless tranceiver over Cypress CY7C65211 USB-to-UART/I2C/SPI/GPIO bus bridge.',
      url='https://github.com/tai/python-ucdev/',
      author='Taisuke Yamada',
      author_email='tai@remove-if-not-spam.rakugaki.org',
      license='Python',
      packages=['ucdev'],
      install_requires=[
          'bitstring',
          'cffi',
          'IPython',
      ]
)
