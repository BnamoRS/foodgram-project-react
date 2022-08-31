from rest_framework.pagination import PageNumberPagination


class UserPaginator(PageNumberPagination):
    page_size_query_param = 'limit'


class SubscriptionPaginator(PageNumberPagination):
    page_size_query_param = 'limit'
