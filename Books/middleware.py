import time

class RequestTimingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - request.start_time

        print(
            f"{request.method} {request.path} took {duration:.4f} seconds"
        )

        return response

from django.conf import settings
from django.http import JsonResponse

class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE:
            return JsonResponse(
                {"Message": "site is under Maintenance"},
                status=503
            )
        response = self.get_response(request)

        return response

class AppHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response['X-App-Name'] = "BooksLibrary"

        return response
        