
This module helps importing to Odoo account move from other systems (like other ERP), using
the Odoo standard XML-RPC API and fully relying on data-treatment methods of `account_invoice_import`.

The use-case it was designed for is the import of customer purchases from an external e-commerce
into Odoo invoices, for a company needing to start Odoo with accounting but slowly transitionning its
e-commerce to Odoo.

Beside import of invoices, this module also handle (compared to OCA module `account_invoice_import`):
- payment import
- creation of contact on-the-fly at invoice import,
  and if needed its delivery and invoice addresses
- delivery address on the invoice
- Additionnal fields on `res.partner`:
    - `title`
    - `street3`, if available (see OCA module `partner_address_street3`)
