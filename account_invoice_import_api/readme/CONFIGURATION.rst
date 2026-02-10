
By default, imported records in Odoo remain editable with no restriction.
However, one might want those imported records to be readonly. To do so,
configure the global settings `import_api.readonly_records` to `True`.

Also, if we want the import to cleverly update Odoo data, you can use
the import config keys `contact_update_on_the_fly` and `contact_update_do_not_erase`.
For more info, please read the docstring of the method `_get_api_config_default`.

Recommended side modules
========================

- `account_invoice_check_total`: to ensure manual verification, when needed, of
   taxes rounding on supplier invoice
- `base_business_document_import_phone`: to allow partner matching by phone
