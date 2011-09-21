from setuptools import setup, find_packages

version = '1.0.0'

setup(name='sbo.policy.deployment',
      version=version,
      description="SBO Site Deployment Policy",
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
          'plone.app.caching',
          'sbo.policy.general',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
