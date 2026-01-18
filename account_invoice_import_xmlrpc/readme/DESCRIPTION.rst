
This module helps importing to Odoo account move from other systems (like other ERP), using
the Odoo standard XML-RPC API and fully relying on data-treatment methods of `account_invoice_import`.

It was designed for a customer needing a slow transition from its ERP to Odoo, who needed to use
Odoo for accounting only but to keep businesse workflow like Sale Order & Invoicing to its
existing external system. The API of this module helped to synchronize Prestashop's paid customer
as validated customer invoices in Odoo.

Beside import of invoices, this module also handle:
- creation of contact on-the-fly of invoice import
- payment import
