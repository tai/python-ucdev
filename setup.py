from setuptools import setup

setup(name='ucdev',
      version='0.0.3',
      description='Library to access various I2C/SPI/GPIO-accessible chips over Cypress CY7C65211/3/5 USB-to-UART/I2C/SPI/GPIO bridge.',
      long_description=open('README.md').read(),
      url='https://github.com/tai/python-ucdev/',
      author='Taisuke Yamada',
      author_email='tai@remove-if-not-spam.rakugaki.org',
      license='MIT',
      packages=['ucdev'],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development :: Embedded Systems',
          'Topic :: System :: Hardware',
      ],
      install_requires=[
          'bitstring',
          'cffi',
          'IPython',
      ]
)
