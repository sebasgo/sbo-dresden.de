from Products.CacheSetup import config
from Products.CacheSetup.Extensions import policy_1, policy_2, policy_3, policy_4

POLICIES = (policy_1, policy_2, policy_3, policy_4)

def updateOldCachePolicy(portal, out):
    ct = getattr(portal, config.CACHE_TOOL_ID)
    rules = getattr(ct, config.RULES_ID, None)
    if rules is not None:
        # this is an old policy
        oldpolicy_id = "old-policy"
        oldpolicy_title = "Old Cache Policy"
        ct.addPolicyFolder(oldpolicy_id, oldpolicy_title)
        policy = getattr(ct, oldpolicy_id)
        folder_ids = [config.RULES_ID, config.HEADERSETS_ID]
        for id in folder_ids:
            oldfolder = getattr(ct, id)
            newfolder = getattr(policy, id)
            cp = oldfolder.manage_copyObjects(oldfolder.objectIds())
            newfolder.manage_pasteObjects(cp)
            newfolder.unmarkCreationFlag()
            for item in newfolder.objectValues():
                item.unmarkCreationFlag()
        ct.setActivePolicyId(oldpolicy_id)
        ct.manage_delObjects(folder_ids)
        # let's also migrate cacheConfig
        cache_config = ct.getCacheConfig()
        if cache_config in ('zserver','apache'):
            ct.setProxyPurgeConfig('no-purge')
        elif cache_config == 'squid':
            ct.setProxyPurgeConfig('no-rewrite')
        else:
            ct.setProxyPurgeConfig('custom-rewrite')

def addCachePolicies(portal, out):
    # We'll extend this later
    # preferably using GenericSetup profiles
    ct = getattr(portal, config.CACHE_TOOL_ID)
    for p in POLICIES:
        ct.addPolicyFolder(p.POLICY_ID, p.POLICY_TITLE)
        rules = ct.getRules(p.POLICY_ID)
        p.addCacheRules(rules)
        header_sets = ct.getHeaderSets(p.POLICY_ID)
        p.addHeaderSets(header_sets)


