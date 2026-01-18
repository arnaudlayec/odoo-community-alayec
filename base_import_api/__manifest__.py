{
    "name": "Base import API (XML-RPC)",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Technical module with base methods and mixin for API import.",
    "author": "Akretion",
    'license': "AGPL-3",
    "website": "https://www.akretion.com",
    "depends": ["base_business_document_import"],
    "data": [
        # security
        "security/base_import_api_security.xml",
        "security/ir.model.access.csv",
        # views
        "views/import_api_call.xml",
        "views/import_api_call_line.xml",
        # templates
        'templates/import_api_template.xml',
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
