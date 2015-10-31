def grab_docs_from(other_func):
    def dec(func):
        if func.__doc__:
            func.__doc__ = func.__doc__ + "\n\n    " + other_func.__doc__
        else:
            func.__doc__ = other_func.__doc__
        return func
    return dec
