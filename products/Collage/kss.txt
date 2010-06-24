KSS support
===========

  >>> helper = portal['front-page'].restrictedTraverse('@@collage_kss_helper')

We use the UID provided by Archetypes as unique identifier:

  >>> helper.getUniqueIdentifier() == portal['front-page'].UID()
  True
