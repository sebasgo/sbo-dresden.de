from Acquisition import aq_parent
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CacheSetup.config import log, CACHE_TOOL_ID, PLONE25
from patch_utils import wrap_method, call_pattern
from cmf_utils import _checkConditionalGET, _setCacheHeaders
try:
    from Products.PageTemplates.DeferExpr import LazyWrapper
except:
    LazyWrapper = None

if PLONE25:
    from zope.app.publisher.interfaces.browser import IBrowserView
else:
    from zope.publisher.interfaces.browser import IBrowserView

#### patch FSPageTemplate.pt_render

# Goal: if a 304 can be determined, rendering the template is cut
# off. Otherwise cache headers are set.

from Products.CMFCore.FSPageTemplate import FSPageTemplate

def FSPT_pt_render(self, source=0, extra_context={}):
    pcs = getToolByName(self, CACHE_TOOL_ID, None)
    # if portal_cache_settings not in place, fall back to the old method
    if pcs is None or not pcs.getEnabled():
        return call_pattern(self, 'pt_render', '__CacheSetup_FSPageTemplate_%s__', source, extra_context)

    self._updateFromFS()  # Make sure the template has been loaded.

    if not source:
        request = self.REQUEST
        object = self.getParentNode()
        view = self.getId()
        member = pcs.getMember()
        (rule, header_set) = pcs.getRuleAndHeaderSet(request, object, view, member)
        if header_set is not None:
            expr_context = rule._getExpressionContext(request, object, view, member, keywords=extra_context)
        else:
            expr_context = None

        # If we have a conditional get, set status 304 and return
        # no content
        if _checkConditionalGET(self, extra_context, rule, header_set, expr_context):
            return ''
        
    result = FSPageTemplate.inheritedAttribute('pt_render')(
        self, source, extra_context
        )
    if not source:
        _setCacheHeaders(self, extra_context, rule, header_set, expr_context)
    return result

#### patch PageTemplate.pt_render

# Goal: actually set the 304 reponse header if applicable.

from Products.PageTemplates.Expressions import getEngine
if PLONE25:
    from TAL.TALInterpreter import TALInterpreter
    from Products.PageTemplates.PageTemplate import \
        PageTemplateTracebackSupplement, PTRuntimeError
else:
    from zope.tal.talinterpreter import TALInterpreter
    from zope.pagetemplate.pagetemplate import \
        PageTemplateTracebackSupplement, PTRuntimeError

def PT_pt_render(self, source=0, extra_context={}):
    """Render this Page Template"""
    pcs = getToolByName(self, CACHE_TOOL_ID, None)
    # if portal_cache_settings not in place, fall back to the old method
    if pcs is None or not pcs.getEnabled():
        return call_pattern(self, 'pt_render', '__CacheSetup_PageTemplate_%s__', source, extra_context)

    if not self._v_cooked:
        self._cook()
    if PLONE25:
        __traceback_supplement__ = (PageTemplateTracebackSupplement, self, self.pt_getContext())
    else:
        __traceback_supplement__ = (PageTemplateTracebackSupplement, self)

    if self._v_errors:
        e = str(self._v_errors)
        raise PTRuntimeError, (
            'Page Template %s has errors: %s' % (self.id, e))

    if not source:
        # If we have a conditional get, set status 304 and return no
        # content
        request = self.REQUEST
        object = self.getParentNode()
        
        # we may get this if we have a Zope 3 browser view
        if IBrowserView.providedBy(object):
            view = getattr(object, '__name__', request['ACTUAL_URL'].split('/')[-1])
            object = aq_parent(object)
        else:
            view = self.getId()
        
        member = pcs.getMember()
        (rule, header_set) = pcs.getRuleAndHeaderSet(request, object, view, member)
        if header_set is not None:
            expr_context = rule._getExpressionContext(request, object, view, member, keywords=extra_context)
        else:
            expr_context = None

        if _checkConditionalGET(self, extra_context, rule, header_set, expr_context):
            return ''
        
    if PLONE25:
        output = self.StringIO()
    else:
        output = StringIO()

    c = self.pt_getContext()
    c.update(extra_context)

    context = getEngine().getContext(c)
    TALInterpreter(self._v_program, self._v_macros,
                   context,
                   output,
                   tal=not source, strictinsert=0)()

    # clean up - XXX
    # try to eliminate circular references - this may be overkill
    if LazyWrapper is not None:
        context._compiler = None
        context.contexts = None
        context.repeat_vars = None
        if PLONE25:
            items = context.global_vars.items()
        else:
            items = context.vars.items()
        for k,v in items:
            if isinstance(v, LazyWrapper):
                v._expr = None
                v._econtext = None
                v._result = None
        if PLONE25:
            if context.vars:
                while len(context.vars):
                    context.vars._pop()
            context.global_vars.clear()
            context.global_vars = None
            context.local_vars.clear()
            context.local_vars = None
        else:
            context.vars.clear()
        context.vars = None
        context._scope_stack = None
    result = output.getvalue()
    if not source:
        _setCacheHeaders(self, extra_context, rule, header_set, expr_context)
    return result


def run():
    log('Applying CMF patches...')
    from Products.PageTemplates.PageTemplate import PageTemplate
    wrap_method(PageTemplate, 'pt_render', PT_pt_render, '__CacheSetup_PageTemplate_%s__')
    from Products.CMFCore.FSPageTemplate import FSPageTemplate
    wrap_method(FSPageTemplate, 'pt_render', FSPT_pt_render, '__CacheSetup_FSPageTemplate_%s__')
    log('CMF Patches applied.')

