# -*- coding: utf-8 -*-

from odoo.addons.account_invoice_import.tests.test_invoice_import import (
    TestInvoiceImport,
)

import odoo
import copy
import json

class TestInvoiceImportApi(TestInvoiceImport):
    """ Largely inspired from tests of `account_invoice_import` module """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.parsed_inv_base = {
            "type": "in_invoice",
            "amount_untaxed": 100.0,
            "amount_total": 101.0,
            "date": "2017-08-16",
            "lines": [
                {
                    "name": "New hi-tech gadget",
                    "qty": 2,
                    "price_unit": 50.0,
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
        cls.journal = cls.env["account.journal"].create({
            "name": "Bank",
            "type": "bank",
            "code": "BKN",
        })

    def _import(self, parsed_inv, config):
        # do the import
        Move = self.env['account.move']
        payload = {
            "data": [dict(self.parsed_inv_base | parsed_inv)],
            "config": dict(config | {"api_raise_exception": True})
        }
        response = Move.import_api(payload)
        # fetch back records & logger for tests
        invoice_ids = response.get("records", {}).get("account.move", {}).get("mapping", {}).values()
        invoices = Move.browse(invoice_ids)
        logger = self.env['import.api.call'].browse(response.get("logger_id"))
        return invoices, logger

    def test_import_invoice(self):
        """ Test account.move creation & validation """
        invoice, _ = self._import({
            "external_ref": "EXT0001",
            "date_due": "2017-08-31",
            "date_start": "2017-08-01",
            "date_end": "2017-08-31",
            "partner": {"name": "Wood Corner"},
        }, {})
        self.assertEqual(invoice.external_ref, "EXT0001")
        self.assertEqual(invoice.state, "posted")

        # without partner: should fail
        _, logger = self._import({}, {})
        self.assertTrue(logger.line_ids.filtered(lambda x: x.state == 'error'))

    def test_import_partner(self):
        """ Test partner:
            1. try move validation without partner creation
            2. partner creation (`invoice_confirm`)
            3. partner match without erasing (`contact_update_do_not_erase`)
        """
        # 1. no creation: save partner data
        street = "1 rue de la Rosée"
        invoice, _ = self._import(
            parsed_inv={
                "external_ref": "EXT0001",
                "partner": {"street": street},
            },
            config={"invoice_confirm": False, "contact_create_on_the_fly": True},
        )
        self.assertFalse(invoice.partner_id)
        self.assertTrue(invoice.import_partner_data["street"], street)

        # 2. creation
        name1 = "Metal Square"
        parsed_inv = {"partner": {"name": name1, "email": "address@company.com"}}
        invoice, _ = self._import(
            parsed_inv=copy.deepcopy(parsed_inv) | {"external_ref": "EXT0002"},
            config={"invoice_confirm": True, "contact_update_on_the_fly": False},
        )
        self.assertEqual(invoice.partner_id.name, name1)

        # 3. match without erasing
        user_human = self.env.user.copy({"name": "Human user"})
        name_modified = "Name edited in UI by human user"
        invoice.partner_id.with_user(user_human).name = name_modified
        invoice, _ = self._import(
            parsed_inv=copy.deepcopy(parsed_inv) | {"external_ref": "EXT0003"},
            config={},
        )
        self.assertEqual(invoice.partner_id.name, name_modified)

    def test_import_payments_invoice(self):
        """ 1. Invoice *with* payments
            2. Invoice *then* payments
        """
        config = {
            "contact_create_on_the_fly": True,
            "invoice_confirm": True,
            "payment_bank_create": True,
            'payment_state': 'paid',
        }
        parsed_inv = {
            "external_ref": 73189,
            "partner": {"name": "Wood Corner"},
            "payments": [
                {
                    "external_ref": 456178,
                    "payment_type": "inbound",
                    "partner": {"name": "Richard Bank"},
                    "journal": {"code": self.journal.code},
                    "amount": 10.0,
                    "date": "2017-09-01",
                    "memo": "Bank tranfer from Richard Bank",
                    "iban": "FR7630001007941234567890185",
                }
            ]
        }
        invoice, _ = self._import(parsed_inv, config)
        self.assertIn(invoice.payment_state, "partial")


    def test_real_data(self):
        """Import different use-case that must be silent"""
        # Test data
        for amount in [0, 5.5, 10, 20]:
            sale_tax_incl = self.sale_tax.copy({
                "name": f"{amount}% VAT incl.",
                "amount": amount,
                "price_include_override": "tax_included",
            })
            self.env["product.product"].create({
                "name": f"TVA{amount}",
                "default_code": f"TVA{amount}",
                "taxes_id": [odoo.Command.set(sale_tax_incl.ids)],
                "supplier_taxes_id": [odoo.Command.set([self.purchase_tax.id])],
                "property_account_income_id": self.income_account.id,
                "property_account_expense_id": self.expense_account.id,
            })
        self.env["account.journal"].create(
            {
                "type": "sale",
                "code": "B2C",
                "name": "Test B2C Journal",
                "sequence": 10,
                "company_id": self.company.id,
            }
        )

        # Json loading
        Move = self.env['account.move']
        file_name = odoo.tools.misc.file_path(
            "account_invoice_import_api/tests/data/invoices.json"
        )
        with open(file_name) as file_res:
            payload = {
                "data": json.load(file_res),
                "config": {"api_raise_exception": True}
            }
            
            # Import
            response = Move.import_api(payload)
            logger = self.env['import.api.call'].browse(response.get("logger_id"))
            
            # Test
            self.assertEqual(logger.to_verify_line_count, 0)
