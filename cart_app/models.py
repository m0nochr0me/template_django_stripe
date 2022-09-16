from django.db import models
from djmoney.models.fields import MoneyField
from decimal import Decimal
from datetime import datetime

from .managers import OrderManager


class Item(models.Model):
    title: str = models.TextField()
    description: str = models.TextField()
    price = MoneyField(max_digits=15, decimal_places=2, default_currency='USD', null=True)
    # price: Decimal = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f'{self.title}'

    def __repr__(self):
        return f'<Item #{self.id}:{self.title}>'


class OrderElement(models.Model):
    item: Item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    qty: int = models.IntegerField(verbose_name='Qty.', default=1)

    def __str__(self):
        return f'{self.item!r}: {self.qty}'

    def __repr__(self):
        return f'<OrderElement #{self.id}>'

    def get_subtotal(self):
        return self.qty * self.item.price

    def get_subtotal_in_sub_unit(self):
        return self.qty * self.item.price.get_amount_in_sub_unit()


class Order(models.Model):
    class PaymentStatusChoices(models.IntegerChoices):
        NEW = 0
        SUCCESS = 1
        PROCESSING = 2
        FAILED = 3

    elements = models.ManyToManyField(OrderElement)
    completed: bool = models.BooleanField(default=False)
    payment_status = models.IntegerField(choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.NEW)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    ts: datetime = models.DateTimeField(null=True)

    objects = OrderManager()

    def __str__(self):
        return f'Order {self.id} {self.ts}'

    def __repr__(self):
        return f'<Order #{self.id}>'

    def __iter__(self):
        return iter(self.elements.all())

    def get_total(self):
        return sum(element.get_subtotal() for element in self)

    def get_total_in_sub_unit(self):
        return sum(element.get_subtotal_in_sub_unit() for element in self)

    def add_element(self, item, qty):
        # if not self.pk:
        self.save()
        element, new = self.elements.get_or_create(item=item, qty=qty)
        element.save()
