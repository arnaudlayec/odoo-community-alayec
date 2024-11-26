/** @odoo-module **/

import { RadioField } from "@web/views/fields/radio/radio_field";
import { useService } from "@web/core/utils/hooks";
import { registry } from '@web/core/registry';

export class RedirectRadioField extends RadioField {
    setup() {
        super.setup();
        this.actionService = useService('action')
    }

    // Overwrites
    onChange(value) {
        super.onChange(value);

        if (value) {
            const context = this.env.model.root.context;
            context.default_project_id = value[0]

            this.actionService.doActionButton({
                type: 'object',
                name: 'button_validate',
                resId: 0,
                resModel: 'project.choice.wizard',
                context: context
            });
        }
    }
}

registry.category('fields').add('project_radio_redirect', RedirectRadioField);
