from .models import Order


class OrderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.order = Order.objects.from_request(request)
        response = self.get_response(request)
        return response

