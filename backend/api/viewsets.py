from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet


class CreateDestroyListViewSet(GenericViewSet, ListModelMixin):
    pass
