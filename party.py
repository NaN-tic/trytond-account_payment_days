#This file is part account_payment_days module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields

__all__ = ['Party']


class Party(ModelSQL, ModelView):
    __name__ = 'party.party'
    customer_payment_days = fields.Char('Customer Payment Days', help='Space '
            'separated list of payment days. A day must be between 1 and 31.')
    supplier_payment_days = fields.Char('Supplier Payment Days', help='Space '
            'separated list of payment days. A day must be between 1 and 31.')

    @classmethod
    def __setup__(cls):
        super(Party, cls).__setup__()
        cls._error_messages.update({
                'invalid_customer_payment_days': ('Invalid customer payment '
                        'days for party "%s".'),
                'invalid_supplier_payment_days': ('Invalid supplier payment '
                        'days for party "%s".'),
                })

    @classmethod
    def validate(cls, parties):
        for party in parties:
            party.check_payment_days()

    def check_payment_days(self):
        def check(days):
            if days:
                try:
                    days = [int(x) for x in days.split()]
                except:
                    return False
                for day in days:
                    if day < 1 or day > 31:
                        return False
            return True

        if not check(self.customer_payment_days):
            self.raise_user_error('invalid_customer_payment_days',
                    (self.rec_name,))

        if not check(self.supplier_payment_days):
            self.raise_user_error('invalid_supplier_payment_days',
                    (self.rec_name,))
