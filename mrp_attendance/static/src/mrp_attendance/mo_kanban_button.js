/** @odoo-module */

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from '@web/core/registry';
import { kanbanView } from '@web/views/kanban/kanban_view';
import { useService } from '@web/core/utils/hooks';
import { _lt } from "@web/core/l10n/translation";

export class MfOrderKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.actionService = useService('action');
    }

    async actionTimesOfToday() {
        this.actionService.doActionButton({
            type: 'object',
            resModel: 'res.users',
            name: 'action_open_mrp_times_today',
            context: this.model.root.context
        });
    }

    async openSignOff() {
        // Go back to Attendance home screen
        this.actionService.doAction({
            name: _lt('Manufacturing Times'),
            type: 'ir.actions.client',
            tag: 'hr_attendance_kiosk_mode',
            target: 'fullscreen',
        }, {
            clearBreadcrumbs: true
        });
    }
}

registry.category("views").add("mrp_attendance_production_kanban", {
    ...kanbanView,
    Controller: MfOrderKanbanController,
    buttonTemplate: "mrp_attendance_production_kanban.KanbanButtons",
});
