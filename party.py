# This file is part account_payment_days module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Party']


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    customer_payment_days = fields.Char('Customer Payment Days', help='Space '
            'separated list of payment days. A day must be between 1 and 31.')
    supplier_payment_days = fields.Char('Supplier Payment Days', help='Space '
            'separated list of payment days. A day must be between 1 and 31.')


    @classmethod
    def validate(cls, parties):
        super(Party, cls).validate(parties)
        for party in parties:
            party.check_payment_days()

    def check_payment_days(self):
        def check(days):
            if days:
                try:
                    days = [int(x) for x in days.split()]
                except ValueError:
                    return False
                for day in days:
                    if day < 1 or day > 31:
                        return False
            return True

        if not check(self.customer_payment_days):
            raise UserError(gettext(
                'account_payment_days.invalid_customer_payment_days',
                    party=self.rec_name))

        if not check(self.supplier_payment_days):
            raise UserError(gettext(
                'account_payment_days.invalid_supplier_payment_days',
                party=self.rec_name))
