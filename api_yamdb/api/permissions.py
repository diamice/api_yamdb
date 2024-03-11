from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Предоставляет доступ только администраторам.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_staff
                 or request.user.role == 'admin')
        )


class IsUAuthenticatedAndPatchMethod(permissions.BasePermission):
    """
    Предоставляет доступ аутенитифированным пользователям на чтение 
    и на изменение своих пользовательских данных.
    """
    def has_permission(self, request, view):
        return (
            (request.method == 'patch' or request.method == 'get')
            and request.user.is_authenticated
        )
