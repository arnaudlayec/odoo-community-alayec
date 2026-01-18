
For a user
==========
A new main-menu "API Import" helps in:
- viewing API calls history
- modify the payload and replay the import directly from Odoo (mostly for debugging)
- investigating issues, thanks to logging of import message
- mark *API calls* as *Reviewed*

Moreover, imported records will have a warning banner telling users the record was imported
(see *Configuration*).

For a developper
================
- exemple of how to use XML-RPC from an external system are given in the module `base_import_api`
- to import invoices, call the `import_api` method of model `account.move` with a user in the group
  `base_import_api.group_import_api_user`
- to import payements: same by targetting the model `account.payment`

Input data format (payload)
===========================
The method `import_api` accepts 1 argument `payload` like this.
{
    "config": {...},
    "data": [{...}],
}

Where:
- `config`: dict of keys:
   - converted to `import_config` for method `account.invoice.import/import_config()`
     (not needed if partner is always matched or created)
   - see for example: `account.move/_get_import_config_default()`
   - plus some configurable keys
- `data`:
   - a list of vals like `parsed_inv` in `account.invoice.import/import_config()`
   - see for example: `fallback_parse_pdf_invoice()`
   - plus `external_id` key

Output data format (response)
=============================
See for example: `import.api.call/_get_api_response()`
