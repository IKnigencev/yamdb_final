from rest_framework import permissions


class IsAuthorOrAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator)


class OnlyReadAndNotUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and not request.user.is_user
        )


class AdminPermission(permissions.BasePermission):
    """
    Проверка, что запрос от лица администратора
    или суперюзера.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and user.is_admin
        )


class ModeratorPermission(permissions.BasePermission):
    """Ограничения для модератора.

    Запрет для user с правами модератора.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or user.is_authenticated and not user.is_moderator
        )
