/** @odoo-module **/

import { RadioField } from "@web/views/fields/radio/radio_field";
import { useService } from "@web/core/utils/hooks";
import { registry } from '@web/core/registry';

export class RedirectRadioField extends RadioField {
    setup() {
        super.setup();
        this.actionService = useService('action')
        this.action = this.env.model.root.context['action'];
        this.contextKeys = this.env.model.root.context['context_keys'] || ['default_project_id'];
    }
    // Overwrites
    onChange(value) {
        if (value) {
            this.redirect(value);
        } else {
            super.onChange(value);
        }
    }

    redirect(project_id) {
        const context = Object.fromEntries(this.contextKeys.map( (key) => [key, project_id[0]]) )
        this.actionService.doAction(
            this.action, {additionalContext: context}
        );
    }
}

registry.category('fields').add('project_radio_redirect', RedirectRadioField);

