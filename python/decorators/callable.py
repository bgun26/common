class entry_exit(object):

    __calls = {}
    MAX_ALLOWED = 1
    def __init__(self, f):
        self.f = f
        num_calls = self.__calls.setdefault(f.__name__, 0)
        if num_calls:
            raise ValueError

    def __call__(self, *args, **kwargs):
        self.__calls[self.f.__name__] += 1
        num_calls = self.__calls[self.f.__name__]
        print("- Entering call #%d for %s" % (num_calls, self.f.__name__))
        if num_calls > self.MAX_ALLOWED:
            raise ValueError
        result = self.f(*args, **kwargs)
        print("- Exited call #%d for %s" % (num_calls, self.f.__name__))
        self.__calls[self.f.__name__] -= 1
        return result

@entry_exit
def func1(val):
    print("inside func1() with %s" % val)
    func1('from F1')
    return 'returning my func1'

@entry_exit
def func2(val):
    print("inside func2() with %s" % val)
    func1('from F2')
    return 'returning my func2'

print(func1('v1'))
print(func2('v2'))

