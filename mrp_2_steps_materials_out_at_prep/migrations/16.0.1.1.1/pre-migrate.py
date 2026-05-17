# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """When ending transitory mode: delete views that were replacing
    'quantity' by 'quantity_minus_outgoing_raw_material'"""
    cr.execute("""
        DELETE FROM ir_ui_view WHERE name IN (
            'stock.quant.inventory.tree.editable.transitory',
            'stock.quant.tree.transitory',
            'stock.quant.form.editable.transitory',
            'stock.quant.pivot.transitory',
            'stock.quant.graph.transitory',
            
            'stock.inventory.conflict.form.view.transitory'
        )
    """)
