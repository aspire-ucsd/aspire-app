import functools

class Register:
    def __init__(self):
        self.registered_fn = {}

    def add(self, action: str):
        def wrapped(fn):
            self.registered_fn[action] = fn
            @functools.wraps(fn)
            def wrapped_f(*args, **kwargs):
                return fn(*args, **kwargs)
            wrapped_f.action = action
            return wrapped_f
        return wrapped