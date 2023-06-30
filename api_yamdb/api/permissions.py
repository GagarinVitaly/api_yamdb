from rest_framework import permissions


class SuperUserOrAdmin(permissions.BasePermission):
    """доступ к ресурсу, если пользователь является
    администратором или суперпользователем."""

    def has_permission(self, request, view):
        return (
            request.user.is_authnticated
            and (request.user.is_superuser
                 or request.user.is_staff
                 or request.user.is_admin))


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class SuperUserOrAdminOrModeratorOrAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authnticated
            and (request.user.is_superuser
                 or request.user.is_staff
                 or request.user.is_admin
                 or request.user.is_moderator
                 or request.user == obj.author))
