from django.contrib import admin

from .models import Item, Order, OrderElement


admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderElement)
