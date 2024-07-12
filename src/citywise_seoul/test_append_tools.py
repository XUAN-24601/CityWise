from tools import seoul_api
import inspect
name=seoul_api.get_api_base_info.name

def is_decorated_function(func):
    """Checks if a function has attributes that suggest it's decorated."""
    # Common attribute set by decorators
    decorated_attrs = ['__wrapped__', '_tool']
    return any(hasattr(func, attr) for attr in decorated_attrs)

# Get a list of all functions in the module
all_functions = [getattr(seoul_api, func) for func in dir(seoul_api)]
for func in all_functions:
    print(func.__name__)
# Filter out decorated functions
decorated_functions = [func for func in all_functions if is_decorated_function(func)]

# Print names of decorated functions
for func in decorated_functions:
    print(func.__name__)
#---------------------------------
def get_member_type(member):
    if inspect.isclass(member):
        return "class"
    elif inspect.isfunction(member):
        return "function"
    elif inspect.ismethod(member):
        return "method"
    elif inspect.isbuiltin(member):
        return "builtin"
    elif inspect.ismodule(member):
        return "module"
    elif inspect.isgeneratorfunction(member):
        return "generator function"
    elif inspect.iscoroutinefunction(member):
        return "coroutine function"
    elif inspect.isasyncgenfunction(member):
        return "asynchronous generator function"
    elif inspect.isroutine(member):
        return "routine"
    else:
        return "unknown"
inspect.getmembers(seoul_api)
APIs=[member for name, member in inspect.getmembers(seoul_api)]
for func in APIs:
    try:
         print(func.name, get_member_type(func))

    except AttributeError:
         print('no')

