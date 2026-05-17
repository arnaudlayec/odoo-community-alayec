
from odoo import models, _
from odoo.exceptions import RedirectWarning

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _pre_button_mark_done(self):
        # Skip PREP check when creating backorders
        if self.env.context.get('skip_backorder'):
            return super()._pre_button_mark_done()

        pickings = self.picking_ids.filtered(lambda x: x.state not in ["done", "cancel"])
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
