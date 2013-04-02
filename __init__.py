#This file is part account_payment_days module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.pool import Pool
from payment_term import *
from invoice import *
from party import *


def register():
    Pool.register(
        Invoice,
        Party,
        PaymentTermLine,
        module='account_payment_days', type_='model')
