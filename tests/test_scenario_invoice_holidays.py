import datetime
import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import (
    create_chart, create_fiscalyear, get_accounts)
from trytond.modules.account_invoice.tests.tools import (
    set_fiscalyear_invoice_sequences)
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):
        today = datetime.date(2026, 1, 1)
        activate_modules(['account_payment_days', 'account_payment_holidays'])

        _ = create_company()
        company = get_company()

        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company, today=today))
        fiscalyear.click('create_period')

        _ = create_chart(company)
        accounts = get_accounts(company)
        receivable = accounts['receivable']
        revenue = accounts['revenue']

        Party = Model.get('party.party')
        PaymentHolidays = Model.get('party.payment.holidays')
        party = Party(name='Party')
        party.customer_payment_days = '30'
        party.payment_holidays.append(PaymentHolidays(
                from_month='08',
                from_day=1,
                thru_month='08',
                thru_day=31,
                ))
        party.save()

        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term = PaymentTerm(name='Three Months')
        line = payment_term.lines.new(type='percent', ratio=Decimal('0.3333333333'))
        line.relativedeltas.new(months=1)
        line = payment_term.lines.new(type='percent', ratio=Decimal('0.3333333333'))
        line.relativedeltas.new(months=2)
        line = payment_term.lines.new(type='remainder')
        line.relativedeltas.new(months=3)
        payment_term.save()

        Invoice = Model.get('account.invoice')
        InvoiceLine = Model.get('account.invoice.line')
        invoice = Invoice(type='out')
        invoice.party = party
        invoice.payment_term = payment_term
        invoice.payment_term_date = datetime.date(2026, 6, 15)
        invoice.invoice_date = datetime.date(2026, 6, 15)
        line = InvoiceLine()
        invoice.lines.append(line)
        line.account = revenue
        line.description = 'Line'
        line.quantity = 1
        line.unit_price = Decimal('300')

        invoice.click('post')
        self.assertEqual(invoice.state, 'posted')

        maturity_dates = sorted(
            line.maturity_date
            for line in invoice.move.lines
            if line.account == receivable)
        self.assertEqual(maturity_dates, [
                datetime.date(2026, 7, 30),
                datetime.date(2026, 9, 30),
                datetime.date(2026, 10, 30),
                ])
