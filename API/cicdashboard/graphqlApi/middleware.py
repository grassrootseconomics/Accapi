from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

# class HealthEndpointMiddleware(MiddlewareMixin):

#     def process_request(self, request):
#         if request.META["PATH_INFO"] == "/health_check":
#         	print(request.META["PATH_INFO"] )
#         	return HttpResponse("OK")


class HealthEndpointMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):

        response = self.get_response(request)
        if request.META["PATH_INFO"] == "/health_check":
        	print(request.META["PATH_INFO"] )
        	return HttpResponse("OK")

        else:
        	return response