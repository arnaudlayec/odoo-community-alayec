/** @odoo-module */

import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";
import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';

/** Transform Workorder tags as button to open Productivity form in a new wizard
 * inspired from `Many2ManyTagsFieldColorEditable`
*/
export class Many2ManyTagsFieldWorkOrder extends Many2ManyTagsField {
    setup() {
        super.setup();
        this.actionService = useService('action');
    }

    getTagProps(record) {
        return {
            ...super.getTagProps(record),
            onClick: (ev) => this.onBadgeClick(ev, record)
        };
    }

    onBadgeClick(ev, record) {
        this.actionService.doActionButton({
            type: 'object',
            resModel: 'mrp.workorder',
            name: 'action_open_productivity_attendance',
            resId: record.resId,
            context: record.model.root.context,
        });
    }
}

Many2ManyTagsFieldWorkOrder.template = "mrp_attendance.Many2ManyTagsFieldWorkOrder";

registry.category("fields").add("many2many_tags_workorder", Many2ManyTagsFieldWorkOrder);
