INSTANCES = dict()


def register(name):
    global INSTANCES

    def fn(cls):
        INSTANCES[name] = cls
        return cls

    return fn


def retrieve(name, **kwargs):
    global INSTANCES
    return INSTANCES[name](**kwargs)
