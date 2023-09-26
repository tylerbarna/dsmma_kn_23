'''
random useful functions
'''
import time

from functools import wraps

def strtime():
    return time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())

def suppress_print(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper