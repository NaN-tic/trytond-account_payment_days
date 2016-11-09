# This file is part account_payment_days module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import payment_term
from . import invoice
from . import party


def register():
    Pool.register(
        invoice.Invoice,
        party.Party,
        payment_term.PaymentTermLine,
        module='account_payment_days', type_='model')
