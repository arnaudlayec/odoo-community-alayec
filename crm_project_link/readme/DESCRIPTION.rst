
This module simply allows to link Opportunities to Projects, with
mirroring `Many2one` fields (1 project for 1 opportunity, 1 opportunity for 1 project).
This can be useful for businesses following a different sale-to-project workflow
than Odoo standard.

Example of use-case:

* Odoo standard: Lead & Opportunity / Quotations & Sales / Projects & Tasks
* Custom business workflow (like construction): Lead & Opportunity / Project / Sales & Purchase orders
