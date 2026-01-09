class ProjectScopedMixin:
    """Mixin to automatically filter and inject project from URL"""

    def get_queryset(self):
        """Filter by project_id from URL"""
        queryset = super().get_queryset()
        project_id = self.kwargs.get("project_id")
        if project_id:
            return queryset.filter(project_id=project_id)
        return queryset

    def get_serializer_context(self):
        """Add project_id to serializer context"""
        context = super().get_serializer_context()
        context["project_id"] = self.kwargs.get("project_id")
        return context
