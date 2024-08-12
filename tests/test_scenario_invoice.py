import datetime
import unittest
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from proteus import Model
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import \
    set_fiscalyear_invoice_sequences
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

        # Set today at the beginning of month (to ensure maturity dates match the test)
        # and in the following month (because maturity dates in the past raise a
        # warning)
        today = datetime.date.today() + relativedelta(day=5, months=1)

        # Install account_payment_days
        activate_modules('account_payment_days')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')
        period = fiscalyear.periods[0]

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create party
        Party = Model.get('party.party')
        party = Party(name='Party')
        party.customer_payment_days = '5 20'
        party.supplier_payment_days = '10 25'
        party.save()
        party_without_days = Party(name='Party Without Days')
        party_without_days.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'service'
        template.list_price = Decimal('40')
        template.account_category = account_category
        product, = template.products
        product.cost_price = Decimal('25')
        template.save()
        product, = template.products

        # Create payment term
        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term = PaymentTerm(name='Term')
        line = payment_term.lines.new(type='percent', ratio=Decimal('.5'))
        line.relativedeltas.new()
        line = payment_term.lines.new(type='remainder')
        line.relativedeltas.new(days=15)
        payment_term.save()

        # Create out invoice and check payment days
        Invoice = Model.get('account.invoice')
        invoice = Invoice()
        invoice.party = party
        invoice.invoice_date = period.start_date
        invoice.payment_term = payment_term
        invoice.payment_term_date = today
        line = invoice.lines.new()
        line.product = product
        line.quantity = 5
        line.unit_price = Decimal('40')
        invoice.click('post')
        self.assertEqual(
            sorted([l.maturity_date.day for l in invoice.lines_to_pay]),
            [5, 20])
        invoice = Invoice()
        invoice.party = party_without_days
        invoice.invoice_date = period.start_date
        invoice.payment_term = payment_term
        invoice.payment_term_date = today
        line = invoice.lines.new()
        line.product = product
        line.quantity = 5
        line.unit_price = Decimal('40')
        invoice.click('post')
        self.assertEqual(sorted([l.maturity_date.day for l in invoice.lines_to_pay]),
                         sorted([(today + relativedelta(days=15)).day, today.day]))

        # Create in invoice and check payment days
        invoice = Invoice()
        invoice.type = 'in'
        invoice.party = party
        invoice.invoice_date = period.start_date
        invoice.payment_term = payment_term
        invoice.payment_term_date = today
        line = invoice.lines.new()
        line.product = product
        line.quantity = 5
        line.unit_price = Decimal('40')
        invoice.click('post')
        self.assertEqual(
            sorted([l.maturity_date.day for l in invoice.lines_to_pay]),
            [10, 25])
        invoice = Invoice()
        invoice.type = 'in'
        invoice.party = party_without_days
        invoice.invoice_date = period.start_date
        invoice.payment_term = payment_term
        invoice.payment_term_date = today
        line = invoice.lines.new()
        line.product = product
        line.quantity = 5
        line.unit_price = Decimal('40')
        invoice.click('post')
        self.assertEqual(
            sorted([l.maturity_date.day for l in invoice.lines_to_pay]),
            sorted([(today + relativedelta(days=15)).day, today.day]))

        #Check search on invoice payment_days field:
        from trytond import backend
        if backend.name == 'postgresql':
            invoices5 = Invoice.find([('payment_days', '=', 5)])
            self.assertEqual(len(invoices5), 1)

            invoices25 = Invoice.find([('payment_days', '=', 25)])
            self.assertEqual(len(invoices25), 1)

            invoices525 = Invoice.find([('payment_days', 'in', [5, 25])])
            self.assertEqual(len(invoices525), 2)
