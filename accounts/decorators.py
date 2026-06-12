from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(predicate):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not predicate(request.user):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


def student_required(function=None, **kwargs):
    actual_decorator = role_required(
        lambda user: user.is_authenticated and user.is_active and user.is_student
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def lecturer_required(function=None, **kwargs):
    actual_decorator = role_required(
        lambda user: (
            user.is_authenticated
            and user.is_active
            and (user.is_lecturer or user.is_superuser)
        )
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_required(function=None, **kwargs):
    actual_decorator = role_required(
        lambda user: user.is_authenticated and user.is_active and user.is_superuser
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
