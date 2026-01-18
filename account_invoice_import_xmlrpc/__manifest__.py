{
    "name": "Account Invoice Import API (XML-RPC)",
    "version": "18.0.1.0.0",
    "summary": "Import in Odoo invoices and payments using native API in XML-RPC.",
    "author": "Akretion",
    'license': "AGPL-3",
    "website": "https://www.akretion.com",
    "depends": ["account_invoice_import", "base_import_api"],
    # recommended modules: `account_invoice_check_total`
    # and `base_business_document_import_phone`
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
