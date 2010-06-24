"""
When using Plone 2.5, we've got to patch Five separately as the page
template patches in patch_cmf are overridden by Five's patches of the
same code.
"""
from Products.CacheSetup.config import log, PLONE25
import Products.CacheSetup.patch_cmf as patch_cmf

def run():
    if not PLONE25:
        # we don't need to do this w/ Z2.10, which uses Z3 PT engine
        return
    
    log('Applying Five patches...')
    from Products.Five.browser.ReuseUtils import rebindFunction
    from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile \
         as Z2PTF
    from Products.Five.browser.TrustedExpression import getEngine

    # CacheFu expects to find the original method on the class as
    # __CacheSetup_PageTemplate_<METHOD_NAME>
    orig_method = getattr(Z2PTF, 'pt_render')
    Z2PTF.__CacheSetup_PageTemplate_pt_render__ = orig_method

    new_pt_render = rebindFunction(patch_cmf.PT_pt_render, getEngine=getEngine)
    Z2PTF.pt_render = new_pt_render
