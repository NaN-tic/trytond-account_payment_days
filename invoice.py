# This file is part account_payment_days module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from sql import Cast
from sql.functions import Function
from sql.conditionals import NullIf
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.model import fields
from trytond import backend

__all__ = ['Invoice']

class RegExpSplitToArray(Function):
    __slots__ = ()
    _function = 'regexp_split_to_array'


class Unnest(Function):
    __slots__ = ()
    _function = 'unnest'


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'
    payment_days = fields.Function(fields.Char('Payment Days'),
        'get_payment_days', searcher='search_payment_days')

    def get_payment_days(self, name):
        if self.type == 'out':
            return self.party.customer_payment_days
        else:
            return self.party.supplier_payment_days

    @classmethod
    def search_payment_days(cls, name, clause):
        Party = Pool().get('party.party')

        if backend.name() == 'sqlite':
            # Sqlite does not support UNNEST function
            return ['OR', [
                    ('type', '=', 'out'),
                    ('party.customer_payment_days',) + tuple(clause[1:]),
                    ], [
                    ('type', '=', 'in'),
                    ('party.supplier_payment_days',) + tuple(clause[1:]),
                    ]]
        party = Party.__table__()
        _, operator, value = clause
        Operator = fields.SQL_OPERATORS[operator]

        customer_days = party.select(party.id,
            Unnest(RegExpSplitToArray(party.customer_payment_days,
                    '\s+')).as_('day'))
        customer_days = customer_days.select(customer_days.id,
            where=(Operator(Cast(NullIf(customer_days.day, ''), 'int'),
                    value)))

        supplier_days = party.select(party.id,
            Unnest(RegExpSplitToArray(party.supplier_payment_days,
                    '\s+')).as_('day'))
        supplier_days = supplier_days.select(supplier_days.id,
            where=(Operator(Cast(NullIf(supplier_days.day, ''), 'int'),
                    value)))

        return ['OR', [
                ('type', '=', 'out'),
                ('party', 'in', customer_days),
                ], [
                ('type', '=', 'in'),
                ('party', 'in', supplier_days),
                ]]

    def get_move(self):
        if self.type == 'out':
            payment_days = self.party.customer_payment_days or ''
        else:
            payment_days = self.party.supplier_payment_days or ''

        payment_days = [int(x) for x in payment_days.split()]
        with Transaction().set_context(account_payment_days=payment_days):
            return super(Invoice, self).get_move()
