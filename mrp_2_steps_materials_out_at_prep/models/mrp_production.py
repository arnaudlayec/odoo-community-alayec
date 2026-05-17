
from odoo import models, _
from odoo.exceptions import RedirectWarning

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _pre_button_mark_done(self):
        pickings = self.picking_ids.filtered(lambda x: x.state not in ["done", "cancel"])
        print("pickings", pickings.read(["name"]))
        if pickings:
            raise RedirectWarning(
                message=_(
                    "Some preparation transfers are still opened. "
                    "You must finish or cancel them before continuing."
                ),
                action=self.action_view_mo_delivery(),
                button_text=_("Open transfers"),
            )
        return super()._pre_button_mark_done()
