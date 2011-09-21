from setuptools import setup, find_packages

version = '1.1.2'

setup(name='sbo.policy.general',
      version=version,
      description="SBO Site Policy",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Sebastian Gottfried',
      author_email='sebastiangottfried@web.de',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sbo', 'sbo.policy'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.iterate',
          'collective.quickupload',
          'sbo.inkstain',
          'sbo.theme',
          'sbo.frontpage',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
