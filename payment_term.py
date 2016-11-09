#This file is part account_payment_days module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from dateutil.relativedelta import relativedelta
from trytond.pool import PoolMeta
from trytond.transaction import Transaction

__all__ = ['PaymentTermLine']


def days_in_month(date):
    return (date + relativedelta(day=31)).day


class PaymentTermLine:
    __name__ = 'account.invoice.payment_term.line'
    __metaclass__ = PoolMeta

    def get_date(self, date):
        '''
        Override function from account_invoice module but check for the
        'account_payment_days' key in context which may contain a list
        of payment days.
        '''
        value = super(PaymentTermLine, self).get_date(date)
        payment_days = Transaction().context.get('account_payment_days')
        if payment_days:
            assert isinstance(payment_days, list)
            payment_days = sorted(payment_days)
            found = False
            for day in payment_days:
                if value.day <= day:
                    if day > days_in_month(value):
                        day = days_in_month(value)
                    value += relativedelta(day=day)
                    found = True
                    break
            if not found:
                day = payment_days[0]
                value += relativedelta(day=day, months=1)
        return value
