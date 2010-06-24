from Products.CacheSetup.config import log

PATTERN = '__CacheSetup_%s__'

def call(self, __name__, *args, **kw):
    return getattr(self, PATTERN % __name__)(*args, **kw)

def call_pattern(self, __name__, pattern=PATTERN, *args, **kw):
    return getattr(self, pattern % __name__)(*args, **kw)


WRAPPER = '__CacheSetup_is_wrapper_method__'
ORIG_NAME = '__CacheSetup_original_method_name__'

def isWrapperMethod(meth):
    return getattr(meth, WRAPPER, False)

def wrap_method(klass, name, method, pattern=PATTERN):
    old_method = getattr(klass, name)
    if isWrapperMethod(old_method):
        log('Not wrapping %s.%s. Already wrapped.' %
            (klass.__name__, name))
        return
    else:
        log('Wrapping %s.%s.' %
            (klass.__name__, name))
    new_name = pattern % name
    setattr(klass, new_name, old_method)
    setattr(method, ORIG_NAME, new_name)
    setattr(method, WRAPPER, True)
    setattr(klass, name, method)

def unwrap_method(klass, name):
    old_method = getattr(klass, name)
    if not isWrapperMethod(old_method):
        raise ValueError, ('Trying to unwrap non-wrapped '
                           'method %s.%s.' % (klass.__name__, name))
    orig_name = getattr(old_method, ORIG_NAME)
    new_method = getattr(klass, orig_name)
    delattr(klass, orig_name)
    setattr(klass, name, new_method)
