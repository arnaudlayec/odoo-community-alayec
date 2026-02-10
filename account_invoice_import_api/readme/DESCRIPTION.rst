
This module helps importing invoices in Odoo from other systems (like other ERP). It rely on
the Odoo standard XML-RPC API and on data-treatment methods of module OCA `account_invoice_import`.

The use-case it was designed for is the import of individual customers purchases from an external
e-commerce website into Odoo invoices (B2C). This company needed to start using Odoo only with
accounting, while slowly transitionning its inventory, logistics and e-commerce to Odoo.

To manage B2C use-cases, this module adds additional import possibilities and features
on top of `account_invoice_import` functionalities:
- import of invoices' payments
- on-the-fly creation of contact at invoice or payment import
- different delivery and invoice addresses on the invoice
- import of additionnal fields on `res.partner` like `title`
