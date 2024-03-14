from rest_framework import permissions


class IsAuthorAdminModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'moderator'
            or request.user.role == 'admin'
        )


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


class ReadOrAdminOnly(permissions.BasePermission):
    """
    Безопасные запросы для анонимного пользователя.
    Или все запросы только для админа и суперпользователя.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.user.role == 'admin'
                         or request.user.is_superuser)
                    )
                )
