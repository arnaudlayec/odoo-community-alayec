# -*- coding: utf-8 -*-

from odoo import exceptions, fields, Command
from odoo.tests import common, tagged, Form
from datetime import timedelta

from odoo.tools import file_open
import base64

@tagged('post_install', '-at_install')
class TestPurchaseMultipleArrivalDate_Base(common.SingleTransactionCase):

    CONFIRMED_DATE = fields.Date.today() + timedelta(days=10)
    FILENAME = 'filename.txt'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Partner
        ResPartner = cls.env['res.partner']
        cls.partner = ResPartner.create({'name': 'Partner'})

        # Project
        cls.project = cls.env['project.project'].create({'name': 'Project Test 01'})

        # Products
        uom_id = cls.env.ref('uom.product_uom_unit').id
        cls.product_stock = cls.env['product.product'].create({
            'name': 'Product Test 01',
            'detailed_type': 'product',
            'uom_id': uom_id,
            'uom_po_id': uom_id
        })
        cls.product_consu = cls.env['product.product'].create({
            'name': 'Product Test 02',
            'detailed_type': 'consu',
            'uom_id': uom_id,
            'uom_po_id': uom_id
        })

        # Purchase Order
        vals = {
            'product_uom': uom_id,
            'product_qty': 1.0,
            'price_unit': 1.0,
            'date_planned': fields.Date.today(),
        }
        cls.order = cls.env['purchase.order'].create({
            'partner_id': cls.env.user.partner_id.id,
            'project_id': cls.project.id,
            'description': 'Purchase Order Test 01',
            'order_line': [Command.create(vals | {
                'name': 'Test Line 01',
                'product_id': cls.product_stock.id,
            }), Command.create(vals | {
                'name': 'Test Line 02',
                'product_id': cls.product_consu.id,
            })]
        })
        cls.line_stock, cls.line_consu = cls.order.order_line

        file_resource = file_open('purchase_multiple_arrival_date/tests/' + cls.FILENAME, 'rb')
        file_content = file_resource.read()
        f = Form(cls.env['purchase.arrival.date'].with_context(
            default_order_id=cls.order.id
        ))
        f.date_arrival = cls.CONFIRMED_DATE
        f.attachment = base64.b64encode(file_content)
        cls.arrival = f.save()
        file_resource.close()


class TestPurchaseMultipleArrivalDate(TestPurchaseMultipleArrivalDate_Base):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    # -- purchase.arrival.date --
    def test_01_arrival_default_lines(self):
        """ Ensure arrival's wizard is prefilled with unconfirmed order lines """
        self.assertEqual(self.arrival.order_line, self.order.order_line)
    
    def test_02_arrival_attachment(self):
        """ Ensure `filename` is written in `ir.attachment` and
            `attachment_id` is written in `purchase.arrival.date`
        """
        filename = '[{}] {}' . format(self.arrival.date_arrival, self.FILENAME)
        self.assertTrue(self.arrival.attachment_id)
        self.assertTrue(self.arrival.attachment_id.name, filename)

    # -- purchase.order.line --
    def test_03_orderline_date_planned_confirmed(self):
        """ Ensure `order.line`.`date_planned` is written
            and lines are confirmed
        """
        self.assertEqual(
            fields.first(self.order.order_line).date_planned.date(),
            self.arrival.date_arrival
        )

    # -- purchase.order --
    def test_04_order_state(self):
        """ Test right computation of order's `date_arrival_state` """
        self.assertEqual(self.order.date_arrival_state, 'ok')
    
    # def test_05_order_attachment_removal(self):
    #     """ Ensure attachment's removal also removes record of `purchase.arrival.date` """
    #     self.order.date_arrival_attachments.unlink()
    #     self.assertFalse(self.order.date_arrival_ids)
    