from .models import Order


def update_order(request):
    if request.session.get('order') != request.order.pk:
        request.session['order'] = request.order.pk
    request.order = Order.objects.from_request(request)


