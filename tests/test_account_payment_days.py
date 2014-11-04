#!/usr/bin/env python
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import unittest
import datetime
from decimal import Decimal
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT, test_view,\
        test_depends
from trytond.transaction import Transaction


class AccountPaymentDaysTestCase(unittest.TestCase):
    'Test AccountPaymentDays module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_payment_days')
        self.payment_term = POOL.get('account.invoice.payment_term')
        self.currency = POOL.get('currency.currency')

    def test0005views(self):
        'Test views'
        test_view('account_payment_days')

    def test0006depends(self):
        'Test depends'
        test_depends()

    def test0010payment_term(self):
        'Test payment_term'
        payment_days = [5, 20]
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as tx:
            with tx.set_context(account_payment_days=payment_days):
                currency, = self.currency.create([{
                            'name': 'cu1',
                            'symbol': 'cu1',
                            'code': 'cu1'
                            }])
                term, = self.payment_term.create([{
                            'name': '30 days, 1 month, 1 month + 15 days',
                            'lines': [
                                ('create', [{
                                            'sequence': 0,
                                            'type': 'percent_on_total',
                                            'divisor': 4,
                                            'percentage': 25,
                                            'days': 30,
                                            }, {
                                            'sequence': 1,
                                            'type': 'percent_on_total',
                                            'divisor': 4,
                                            'percentage': 25,
                                            'months': 1,
                                            }, {
                                            'sequence': 2,
                                            'type': 'fixed',
                                            'months': 1,
                                            'days': 30,
                                            'amount': Decimal('396.84'),
                                            'currency': currency.id,
                                            }, {
                                            'sequence': 3,
                                            'type': 'remainder',
                                            'months': 2,
                                            'days': 30,
                                            'day': 15,
                                            }])
                                ]}])
                terms = term.compute(Decimal('1587.35'), currency,
                        date=datetime.date(2011, 10, 1))
                self.assertEqual(terms, [
                        (datetime.date(2011, 11, 05), Decimal('396.84')),
                        (datetime.date(2011, 11, 05), Decimal('396.84')),
                        (datetime.date(2011, 12, 05), Decimal('396.84')),
                        (datetime.date(2012, 01, 20), Decimal('396.83')),
                        ])


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountPaymentDaysTestCase))
    return suite
