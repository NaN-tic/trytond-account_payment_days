# This file is part account_payment_days module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.transaction import Transaction

__all__ = ['Invoice']


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    def get_move(self):
        if self.type == 'out':
            payment_days = self.party.customer_payment_days or ''
        else:
            payment_days = self.party.supplier_payment_days or ''

        payment_days = [int(x) for x in payment_days.split()]
        with Transaction().set_context(account_payment_days=payment_days):
            return super(Invoice, self).get_move()
