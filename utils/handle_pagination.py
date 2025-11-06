from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'
    # max_page_size = 100

    def get_paginated_response(self, data):
        current_page = self.page.number
        total_pages = self.page.paginator.num_pages

        last_page_link = None
        if total_pages > 1:
            last_page_link = self.request.build_absolute_uri(f'?page={total_pages}')

        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'current_page': current_page,
            'next_page': current_page + 1 if self.page.has_next() else 0,
            'last_page': current_page - 1 if self.page.has_previous() else 0,
            'last_page_link': last_page_link,
            'results': data
        })
