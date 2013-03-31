#The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL
from trytond.transaction import Transaction

__all__ = ['Invoice']


class Invoice(ModelSQL, ModelView):
    __name__ = 'account.invoice'

    def create_move(self):
        if self.type in ('out_invoice', 'out_credit_note'):
            payment_days = self.party.customer_payment_days
        else:
            payment_days = self.party.supplier_payment_days

        if payment_days:
            payment_days = [int(x) for x in payment_days.split()]

        with Transaction().set_context(account_payment_days=payment_days):
            return super(Invoice, self).create_move()
