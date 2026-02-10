
For a user
==========

Imported records have a top-warning banner informing users the record was imported.

A new main-menu "API Import" helps in:
- viewing API calls history
- investigating issues, thanks to logging of import message
- mark *API calls* as *Reviewed*
- for API admins, modify the payload and replay the import directly from Odoo (mostly for debugging)

For a developper
================

To format the data in the proper JSON format, see `base_import_api` specifications.
They also explain how to interprete the API response.

This module adds the endpoint `import_api` on the 2 models:
- `account.move`: to import invoices, customers & suppliers,
  shipping and invoicing addresses and payments (e.g. Paypal, credit card).
- `account.payment`: to import payments *after* the invoices (e.g. bank transfer, checks, cash)

Please review demo data for full documentation on configurations and data specifications.
