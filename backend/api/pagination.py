from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Custom Paginator."""

    page_size = 6
    page_size_query_param = "limit"