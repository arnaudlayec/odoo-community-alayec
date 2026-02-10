
Official Odoo documentation
===========================

To see how communicate with Odoo XML-RPC from an external tool:
https://www.odoo.com/documentation/master/developer/reference/external_rpc_api.html


Permissions
===========

The account used in the XML-RPC call must be in the group
`base_import_api.group_import_api_manager`.

Response format
===============

Read at `_get_api_response` method.


Example
=======

```python
payload = {
    "config": {
        "api_raise_exception": False,
        'origin': "My External Software",
        "company": 1,
    },
    "data": [
        {
            // invoice 1
        },
        {
            // invoice 2
        }
    ]
}
response = models.execute_kw(
    db, uid, password, 'account.move', 'import_api', payload
)

print("Import done, status is '%s': %s" % (response["state"], response["state_text"]))
plain_report = response["report"]
mapped_invoices = response["records"].get("account.move", {}).get("mapping", {})

```
