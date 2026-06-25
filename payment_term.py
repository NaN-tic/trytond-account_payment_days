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
        transaction = Transaction()
        base_date = date
        for relativedelta_ in self.relativedeltas:
            base_date += relativedelta_.get()

        nominal_date = self.next_payment_day(base_date)
        final_date = nominal_date
        if (transaction.context.get('account_payment_holidays')
                and hasattr(self, 'next_working_day')):
            working_date = self.next_working_day(final_date)
            while final_date != working_date:
                final_date = self.next_payment_day(working_date)
                working_date = self.next_working_day(final_date)

        state_key = (
            self.payment.id if self.payment else None,
            date,
            tuple(transaction.context.get('account_payment_days') or ()),
            tuple(transaction.context.get('account_payment_holidays') or ()),
            )
        state = getattr(transaction, '_account_payment_days_state', None)
        if (state
                and state.get('key') == state_key
                and state['base_date'] < base_date
                and state['nominal_date'] < state['final_date']
                and final_date <= state['final_date']):
            final_date = self.next_payment_day(
                state['final_date'] + relativedelta(days=1))
            if (transaction.context.get('account_payment_holidays')
                    and hasattr(self, 'next_working_day')):
                working_date = self.next_working_day(final_date)
                while final_date != working_date:
                    final_date = self.next_payment_day(working_date)
                    working_date = self.next_working_day(final_date)
        transaction._account_payment_days_state = {
            'key': state_key,
            'base_date': base_date,
            'nominal_date': nominal_date,
            'final_date': final_date,
            }
        return final_date
