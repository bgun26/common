import datetime

def get_obj_name_and_type(obj):
    obj_name = getattr(obj, '__name__', None)
    if obj_name:
        obj_type = 'class'
    else:
        obj_name = type(obj).__name__
        obj_type = 'instance of'
    return obj_name, obj_type

class MyVars(object):
    calls = {}

# @classmethod or @staticmethod decorators have to be applied last/on top
def track_unreturned_calls_to_method(max_allowed=1):
    def real_decorator(method):
        def decorated(*args, **kwargs):
            method_parent = args[0]
            method_name = method.__name__
            parent_name, parent_type = get_obj_name_and_type(method_parent)
            key = (parent_name, method_name)

            MyVars.calls.setdefault(key, 0)
            MyVars.calls[key] += 1
            num_calls = MyVars.calls[key]

            if num_calls > max_allowed:
                raise RecursionError("Unreturned calls exceeded limit for %s, %s" % (key[0], key[1]))
            print("Call #%d to func %s from %s %s" % (num_calls, method_name, parent_type, parent_name))

            method_return = method(*args, **kwargs)

            print("Returned call #%d to func %s from %s %s" % (num_calls, method_name, parent_type, parent_name))
            MyVars.calls[key] -= 1
            return method_return
        return decorated
    return real_decorator
