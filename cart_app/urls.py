from django.urls import path

from .views import index, stipe_config, item_detail, order_detail, payment_result, stripe_webhook

app_name = 'cart_app'

urlpatterns = [
    path('', index, name='index'),
    path('config/', stipe_config, name='stripe_config'),
    path('item/<int:pk>', item_detail, name='item_detail'),
    path('order/<int:pk>', order_detail, name='order_detail'),
    path('result/', payment_result, name='payment_result'),
    path('wh/', stripe_webhook, name='stripe_webhook')
]
