from Products.Collage.content._collage import Collage
from Products.Collage.content._row import CollageRow
from Products.Collage.content._column import CollageColumn
from Products.Collage.content._alias import CollageAlias

from Products.Collage.interfaces import ICollageAlias

from zope.component import adapter
from zope.app.event.interfaces import IObjectModifiedEvent

@adapter(ICollageAlias, IObjectModifiedEvent)
def updateCollageAliasLayout(context, event):
    target = context.get_target()
    if target:
        layout = target.getLayout()
        context.setLayout(layout)
