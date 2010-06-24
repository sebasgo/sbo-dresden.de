import htmlentitydefs

"""
Unicode to HTML entity-converter (neccesary for IE6)
"""

codepoint2entity = {}
safe_characters = ['<', '>', '"', '&'] 
for c in htmlentitydefs.codepoint2name:
    if c not in map(ord, safe_characters): # skip "safe" characters
        codepoint2entity[c] = '&%s;' % unicode(htmlentitydefs.codepoint2name[c])

def escape_to_entities(string):
    ustr = string.translate(codepoint2entity)
    result = []
    for s in ustr:
        if ord(s) > 0x7f:
            s = '&#%d;' % ord(s)
        result.append(s)
    
    return "".join(result)
