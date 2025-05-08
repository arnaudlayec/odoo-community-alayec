/** @odoo-module */

import { registry } from "@web/core/registry";
import { Many2ManyBinaryField } from "@web/views/fields/many2many_binary/many2many_binary_field";

export class Many2ManyBinaryFieldOpen extends Many2ManyBinaryField {
    setup () {
        super.setup();
    }

    getUrl(id) {
        return "/web/content/" + id;
    }
}

registry.category("fields").remove("many2many_binary");
registry.category("fields").add("many2many_binary", Many2ManyBinaryFieldOpen);
