# This file is part of the account_payment_days module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
import datetime
import unittest
import doctest

import trytond.tests.test_tryton
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import doctest_teardown
from trytond.tests.test_tryton import doctest_checker
from trytond.transaction import Transaction


class AccountPaymentDaysTestCase(ModuleTestCase):
    'Test Account Payment Days module'
    module = 'account_payment_days'

    @with_transaction()
    def test0010payment_term(self):
        'Test payment_term'
        pool = Pool()
        PaymentTerm = pool.get('account.invoice.payment_term')
        Currency = pool.get('currency.currency')
        payment_days = [5, 20]
        currency, = Currency.create([{
                    'name': 'cu1',
                    'symbol': 'cu1',
                    'code': 'cu1'
                    }])

        term, = PaymentTerm.create([{
                    'name': '30 days, 1 month, 1 month + 15 days',
                    'lines': [
                        ('create', [{
                                    'sequence': 0,
                                    'type': 'percent_on_total',
                                    'divisor': 4,
                                    'ratio': Decimal('.25'),
                                    'relativedeltas': [
                                        ('create', [{
                                                    'days': 30,
                                                    }])],
                                    }, {
                                    'sequence': 1,
                                    'type': 'percent_on_total',
                                    'divisor': 4,
                                    'ratio': Decimal('.25'),
                                    'relativedeltas': [
                                        ('create', [{
                                                    'months': 1,
                                                    }])],
                                    }, {
                                    'sequence': 2,
                                    'type': 'fixed',
                                    'amount': Decimal('396.84'),
                                    'currency': currency.id,
                                    'relativedeltas': [
                                        ('create', [{
                                                    'months': 1,
                                                    'days': 30,
                                                    }])],
                                    }, {
                                    'sequence': 3,
                                    'type': 'remainder',
                                    'relativedeltas': [
                                        ('create', [{
                                                    'months': 2,
                                                    'days': 30,
                                                    'day': 15,
                                                    }])],
                                    },
                                ])],
                    }])

        with Transaction().set_context(account_payment_days=payment_days):
            terms = term.compute(Decimal('1587.35'), currency,
                    date=datetime.date(2011, 10, 1))
            self.assertEqual(terms, [
                    (datetime.date(2011, 11, 5), Decimal('396.84')),
                    (datetime.date(2011, 11, 5), Decimal('396.84')),
                    (datetime.date(2011, 12, 5), Decimal('396.84')),
                    (datetime.date(2012, 1, 20), Decimal('396.83')),
                    ])


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountPaymentDaysTestCase))
    suite.addTests(doctest.DocFileSuite(
            'scenario_invoice.rst',
            tearDown=doctest_teardown, encoding='utf-8',
            checker=doctest_checker,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
