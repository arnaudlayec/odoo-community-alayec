
This module adds a required *Project* field on Manufacturing Orders and related documents.
This is useful for business verticals likes Construction which production is almost
only project-oriented.

It also adds:
* a *Manufacturing Orders* Smart-Button on Project form
* a related *Project* field on `form` and `tree` view of:
    * Work Orders
    * Manufacturing Times
    * Stock Picking
    * Stock Move (and Lines)
    * Stock Valuation Layers (depency with native Odoo CE module `stock_account`)
