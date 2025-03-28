from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def paginate_queryset(self, queryset, request, view=None):
        return super().paginate_queryset(queryset, request, view)