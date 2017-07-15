from functools import wraps
from flask import abort
from flask_login import current_user

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorator_function(*arg,**kwargs):
            is not current_user.can(permission):
                abort(403)
            return f(*arg,**kwargs)
        return decorator_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINSTER)(f)
