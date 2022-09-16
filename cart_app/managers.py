from django.db.models import Manager
from django.utils.timezone import now
from datetime import datetime, timedelta


class OrderManager(Manager):

    def from_request(self, request):
        order_id = request.session.get('order', None)
        order = self.current().filter(id=order_id)
        last_update = now()

        if order_id and order.update(ts=last_update):
            self.expired().delete()
        elif order_id:
            del request.session['order']
            order_id = None

        return self.model(id=order_id, ts=last_update)

    def expire_time(self):
        return now() - timedelta(minutes=60)

    def current(self):
        return self.filter(ts__gte=self.expire_time())

    def expired(self):
        return self.filter(ts__lt=self.expire_time())
