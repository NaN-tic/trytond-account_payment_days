import datetime
import unittest
from decimal import Decimal

from dateutil.relativedelta import relativedelta
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
        today = datetime.date.today()
        holiday_date = today + relativedelta(months=1, day=1)
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
                from_month=f'{holiday_date.month:02}',
                from_day=1,
                thru_month=f'{holiday_date.month:02}',
                thru_day=31,
                ))
        party.save()

        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term = PaymentTerm(name='Three Months')
        line = payment_term.lines.new(type='percent', ratio=Decimal('0.33333333'))
        line.relativedeltas.new(months=1)
        line = payment_term.lines.new(type='percent', ratio=Decimal('0.33333333'))
        line.relativedeltas.new(months=2)
        line = payment_term.lines.new(type='remainder')
        line.relativedeltas.new(months=3)
        payment_term.save()

        Invoice = Model.get('account.invoice')
        InvoiceLine = Model.get('account.invoice.line')
        invoice = Invoice(type='out')
        invoice.party = party
        invoice.payment_term = payment_term
        invoice.payment_term_date = today.replace(day=1)
        invoice.invoice_date = today
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
        maturity_date = holiday_date + relativedelta(months=1, day=30)
        self.assertEqual(maturity_dates, [
                maturity_date,
                maturity_date + relativedelta(months=1, day=30),
                maturity_date + relativedelta(months=2, day=30),
                ])
