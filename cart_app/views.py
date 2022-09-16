from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponse

import json
import stripe

from .models import Item, Order
from .forms import AddToOrder
from .utils import update_order

stripe.api_key = settings.STRIPE_SK


def index(request):
    template_name = 'cart/index.html'
    items = Item.objects.all()
    context = {'items': items}
    return render(request, template_name, context)


@csrf_exempt
def stipe_config(request):
    if request.method == 'GET':
        conf = {'publicKey': settings.STRIPE_PK}
        return JsonResponse(conf, safe=False)


@csrf_exempt
def stripe_webhook(request):
    if request.method == 'POST':
        wh_secret = settings.STRIPE_WH
        payload = request.body
        sig_header = request.headers.get('stripe-signature')

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, wh_secret)
        except stripe.error.SignatureVerificationError as e:
            print(f'Webhook error: {e}')
            return JsonResponse({'success': False})

        event_resource, event_type = event['type'].split('.')

        if event_resource == 'payment_intent':
            intent_id = event['data']['object']['id']
            order = Order.objects.get(payment_id=intent_id)
            if event_type == 'succeeded':
                order.payment_status = Order.PaymentStatusChoices.SUCCESS
            elif event_type == 'processing':
                order.payment_status = Order.PaymentStatusChoices.PROCESSING
            elif event_type == 'payment_failed':
                order.payment_status = Order.PaymentStatusChoices.FAILED
            order.save()
        else:
            print(f"Unhandled event {event['type']}")

        return JsonResponse({'success': True})
    else:
        return HttpResponseNotAllowed('Method not allowed')


@csrf_exempt
def payment_result(request):
    if request.method == 'GET':
        intent_id = request.GET.get('payment_intent', None)
        if not intent_id:
            return HttpResponseBadRequest('Payment Intent Expected')
        # stripe.api_key = settings.STRIPE_SK
        payment_intent = stripe.PaymentIntent.retrieve(intent_id)

        context = {'result': payment_intent.status}
        template_name = 'cart/result.html'
        return render(request, template_name, context)


def order_detail(request, pk):
    template_name = 'cart/order.html'
    order = get_object_or_404(Order, pk=pk)
    # stripe.api_key = settings.STRIPE_SK

    # intent_id = request.session.get('intent_id', None)
    intent_id = order.payment_id

    if intent_id:
        payment_intent = stripe.PaymentIntent.retrieve(intent_id)
    else:
        payment_intent = stripe.PaymentIntent.create(
            amount=order.get_total_in_sub_unit(),
            currency=order.get_total().currency or 'usd',
            payment_method_types=['card'])
        # request.session['intent_id'] = payment_intent.id
        order.payment_id = payment_intent.id
        order.save()

    if request.method == 'POST':
        return HttpResponseNotAllowed('Method not allowed')

    context = {'order': order,
               'client_secret': payment_intent.client_secret}
    return render(request, template_name, context)


def item_detail(request, pk):
    template_name = 'cart/item.html'
    item = get_object_or_404(Item, pk=pk)
    add_to_order_form = AddToOrder(request.POST or None, initial={'qty': 1})

    if request.method == 'POST':
        if add_to_order_form.is_valid():
            qty = add_to_order_form.cleaned_data['qty']
            request.order.add_element(item=item, qty=qty)
            update_order(request)
            return redirect('cart_app:index')

    context = {'item': item,
               'add_form': add_to_order_form}

    return render(request, template_name, context)


