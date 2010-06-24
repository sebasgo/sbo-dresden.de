Collage
=======

:: compatibility

   Plone 3.1
   Five 1.5

:: about

Collage is a product for aggregating and displaying multiple content items on
a single page.

It provides the following content-types:

  * Collage
  * Row
  * Column
  * Alias

The first three are structural containers that provide basic layouting
functionality. The premise is that a column fits inside a row which again
fits inside a collage.

The Alias-type is provided to allow displaying existing objects from the site
inside the collage.

:: javascript-functionality

We use the jquery-library to facilitate easy scripting. Ajax is used to move
content items, columns and rows around without reloading the page.

:: status

Used in production.

:: support for add-on packages

These should be added to the collective.collage package:

* https://svn.plone.org/svn/collective/collective.collage

under ./browser/addons/<package name>

Make sure collective.collage is in your python path if you want these views
registered for use in Collage.

:: credits

Malthe Borch (main developer) <mborch@gmail.com>
Pelle Kroegholt <pelle@headnet.dk>
Sune Toft <sune@headnet.dk>

:: sponsors

Work on this product has been sponsored by Headnet (http://www.headnet.dk).
