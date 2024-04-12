"""
自定义 ViewSets
"""
from rest_framework.viewsets import GenericViewSet
from utils import mixins


class ReadOnlyModelViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    只读 ViewSet
    """
    pass


class ModelViewSet(mixins.GetSerializerClassMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    可读写 ViewSet
    不同 Action 可指定不同 Serializer
    """
    pass
