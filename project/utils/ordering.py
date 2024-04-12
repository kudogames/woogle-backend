from rest_framework import filters


class CamelCaseOrderingFilter(filters.OrderingFilter):
    """
    ordering 查询参数将值小驼峰转为下划线
    """

    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get(self.ordering_param)
        if ordering:
            return queryset.order_by(self.camel_to_underscore(ordering))
        return queryset

    @staticmethod
    def camel_to_underscore(name):
        """
        将小驼峰式的字段名转换为下划线式的字段名
        """
        return ''.join(['_' + i.lower() if i.isupper() else i for i in name]).lstrip('_')
