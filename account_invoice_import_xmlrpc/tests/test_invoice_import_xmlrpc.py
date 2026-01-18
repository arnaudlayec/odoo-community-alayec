# -*- coding: utf-8 -*-

from odoo.tests import new_test_user
from odoo.addons.account_invoice_import.tests.test_invoice_import import (
    TestInvoiceImport,
)

class TestInvoiceImportXmlRpc(TestInvoiceImport):
    """ Largely inspired from tests of `account_invoice_import` module """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.external_id = "EXT001"
        cls.vals_base = {
            "external_id": cls.external_id,
            "type": "in_invoice",
            "amount_untaxed": 100.0,
            "amount_total": 101.0,
            "date": "2017-08-16",
            "description": "New hi-tech gadget",
            "lines": [
                {
                    "name": "Super test",
                    "qty": 2,
                    "price_unit": 50,
                    "taxes": [
                        {
                            "amount_type": "percent",
                            "amount": 1.0,
                            "unece_type_code": "VAT",
                            "unece_categ_code": "S",
                        }
                    ],
                }
            ],
        }

    def _import(self, vals, config):
        # do the import
        Move = self.env['account.move']
        payload = {
            "data": [dict(self.vals_base | vals)],
            "config": dict(config)
        }
        response = Move.import_api(payload)
        # fetch back invoices & logger for tests
        invoices = Move.browse(response.get("mapped_ids", {}).values())
        logger = self.env['import.api.call'].browse(response.get("logger_id"))
        return invoices, logger

    def test_import_in_invoice_xmlrpc(self):
        """ Test account.move creation & validation """
        invoice, _ = self._import({
            "date_due": "2017-08-31",
            "date_start": "2017-08-01",
            "date_end": "2017-08-31",
            "partner": {"name": "Wood Corner"},
        }, {})
        self.assertEqual(invoice.external_id, self.external_id)
        self.assertEqual(invoice.state, "posted")

        # without partner: should fail
        _, logger = self._import({}, {})
        self.assertTrue(logger.line_ids.filtered(lambda x: x.state == 'error'))

    def test_partner_import(self):
        """ Test partner:
            1. move validation without creation
            2. partner match & update (`invoices_confirm` and `_match_or_import_partner`)
            3. partner match without erasing (`contact_update_do_not_erase`)
        """
        # 1. save partner data
        email = "address@company.com"
        invoice, _ = self._import(
            vals={"partner": {"email": email},},
            config={"invoices_confirm": False, "contact_create_on_the_fly": False},
        )
        self.assertFalse(invoice.partner_id)
        self.assertTrue(invoice.import_partner_data["email"], email)

        # 2.
        name1 = "Metal Square"
        vals = {"partner": {"name": name1, "email": email}}
        invoice, _ = self._import(dict(vals), {}) # invoices_confirm: True (default)
        self.assertTrue(invoice.partner_id)

        # 3.
        user_human = self.env.user.copy({"name": "Human user"})
        name2 = "Name edited in UI by human user"
        invoice.partner_id.with_user(user_human).name = name2
        invoice, _ = self._import(dict(vals), {})
        self.assertEqual(invoice.partner_id.name, name2)
