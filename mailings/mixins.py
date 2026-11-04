from django.core.exceptions import PermissionDenied


class OwnerRequiredMixin:
    """Разрешает изменение объекта только владельцу или суперпользователю."""

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_superuser:
            raise PermissionDenied("Нельзя изменять чужой объект.")
        return super().dispatch(request, *args, **kwargs)
