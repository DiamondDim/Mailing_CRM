from django.core.exceptions import PermissionDenied


class OwnerRequiredMixin:
    """
    Миксин для проверки прав доступа.
    - Менеджеры (is_staff) могут просматривать всё, но не могут редактировать/удалять чужое.
    - Обычные пользователи могут работать только со своими объектами.
    """

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Если пользователь не является владельцем объекта
        if obj.owner != request.user:
            # И при этом он не суперпользователь/менеджер
            if not request.user.is_staff:
                raise PermissionDenied("У вас нет прав для управления этим объектом.")

            # Если он менеджер (is_staff), он может просматривать (GET),
            # но не может изменять или удалять (POST/PUT/DELETE)
            if request.method != 'GET':
                raise PermissionDenied("Менеджеры не могут редактировать или удалять чужие данные.")

        return super().dispatch(request, *args, **kwargs)
