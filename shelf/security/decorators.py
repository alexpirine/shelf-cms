from flask_security import current_user

def allow_superadmin(func):
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.has_role('superadmin'):
            return True
        else:
            return func(*args, **kwargs)

    return wrapper
