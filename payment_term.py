# This file is part account_payment_days module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from dateutil.relativedelta import relativedelta
from trytond.pool import PoolMeta
from trytond.transaction import Transaction

__all__ = ['PaymentTermLine']


def days_in_month(date):
    return (date + relativedelta(day=31)).day


class PaymentTermLine(metaclass=PoolMeta):
    __name__ = 'account.invoice.payment_term.line'

    def next_payment_day(self, date):
        payment_days = Transaction().context.get('account_payment_days')
        if payment_days:
            assert isinstance(payment_days, list)
            payment_days = sorted(payment_days)
            found = False
            for day in payment_days:
                if date.day <= day:
                    if day > days_in_month(date):
                        day = days_in_month(date)
                    date += relativedelta(day=day)
                    found = True
                    break
            if not found:
                day = payment_days[0]
                date += relativedelta(day=day, months=1)
        return date

    def get_date(self, date):
        '''
        Override function from account_invoice module but check for the
        'account_payment_days' key in context which may contain a list
        of payment days.
        '''
        date = super(PaymentTermLine, self).get_date(date)
        date = self.next_payment_day(date)
        if Transaction().context.get('account_payment_holidays'):
            working_date = self.next_working_day(date)
            while date != working_date:
                date = self.next_payment_day(working_date)
                working_date = self.next_working_day(date)
        return date
