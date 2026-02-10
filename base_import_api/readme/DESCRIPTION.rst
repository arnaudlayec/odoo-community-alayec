
This module does not provide any business features by itself.
This is a base module providing 2 things:
* a mixin `base.import.api.mixin`. Models inheriting it get an
  public XML-RPC exposed method `import_api` which can receive
  a JSON payload to import data through the logic offered by this
  module. See the example in `account_invoice_import_api` and logic
  in `_run_import_api()`.
* end-user interface to review API calls history, imported records and
  ease debugging.

Note: XML-RPC API will be deprecated in Odoo v20.0.
Credits: module icon to Freepik.
