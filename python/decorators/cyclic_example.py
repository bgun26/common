from decorators import track_unreturned_calls_to_method

class Singleton(type):
    _instances = {}
    @track_unreturned_calls_to_method(max_allowed=2)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class BaseClass(metaclass=Singleton):
    def __init__(self, through):
        self._base_val = 'BASE'
        print("Init %s through %s" % (self._base_val, through))
        self._deps = None
        self.base_initalizer()
    
    @track_unreturned_calls_to_method(max_allowed=1)
    def base_initalizer(self):
        print("base_initializer through %s" %  self)

    @classmethod
    @track_unreturned_calls_to_method(max_allowed=1)
    def set_common_params(cls):
        print("set_common_params through %s" %  cls)

class MyClassA(BaseClass):
    def __init__(self):
        self._a_val = 'Class A'
        print("Init %s" % self._a_val)
        BaseClass.__init__(self, self._a_val)
        self._deps = [MyClassC()]
        # self._deps = []

class MyClassB(BaseClass):
    def __init__(self):
        self._b_val = 'Class B'
        print("Init %s" % self._b_val)
        BaseClass.__init__(self, self._b_val)
        self._deps = [MyClassA()]

class MyClassC(BaseClass):
    def __init__(self):
        self._c_val = 'Class C'
        print("Init %s" % self._c_val)
        BaseClass.__init__(self, self._c_val)
        # self._deps = [MyClassB()]
        self._deps = [MyClassA(), MyClassB()]

try:
    BaseClass.set_common_params()
    inst = MyClassC()
    BaseClass.set_common_params()
except RecursionError as e:
    print("EXCEPTION: %s" % str(e))
finally:
    # print(globals())
    exit
