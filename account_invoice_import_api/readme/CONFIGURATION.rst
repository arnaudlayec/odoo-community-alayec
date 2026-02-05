
By default, imported records in Odoo remain editable with no restriction.
However, we might want those imported records to be readonly. To do so,
configure the global settings `import_api.readonly_records` to `True`.

Also, if we want the import to cleverly update Odoo data, you can use
the import config keys `contact_update_on_the_fly` and `contact_update_do_not_erase`.
For more info, please read `_get_api_config_default`.
