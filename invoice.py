# This file is part account_payment_days module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from functools import wraps
from trytond.model import ModelView, ModelSQL
from trytond.transaction import Transaction

__all__ = ['Invoice']


def process_payment_days(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.type == 'out':
            payment_days = self.party.customer_payment_days
        else:
            payment_days = self.party.supplier_payment_days

        if payment_days:
            payment_days = [int(x) for x in payment_days.split()]

        with Transaction().set_context(account_payment_days=payment_days):
            return func(self, *args, **kwargs)
    return wrapper


class Invoice(ModelSQL, ModelView):
    __name__ = 'account.invoice'

    @process_payment_days
    def create_move(self):
        # This method is called when not issuing invoice_speedup.patch
        # XXX: Remove when patch is commited in core and avoid decorator
        return super(Invoice, self).create_move()

    @process_payment_days
    def get_move(self):
        # This method is called when using invoice_speedup.patch
        return super(Invoice, self).get_move()
