/** @odoo-module **/

const { Component, useState, onWillStart } = owl;
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

// --- DropDown Item (project) ---
export class SystrayFavProjectsItem extends Component {
    setup () {
        this.orm = useService("orm");
        this.action = useService("action");

        this.project = useState(this.props.project);
    }
    
    toggleProject() {
        // Update
        this.orm.call("project.project", 'toggle_favorite', [this.project.id]);
        this.project.is_favorite = !this.project.is_favorite;
        
        // Reload displayed component
        this.action.doAction({
            'type': 'ir.actions.client',
            'tag': 'soft_reload'
        });
    }
}
SystrayFavProjectsItem.template = "project.SystrayFavProjectsItem";
SystrayFavProjectsItem.components = { DropdownItem };
SystrayFavProjectsItem.props = {
    project: {type: Object}
};


// --- Systray (list) ---
export class SystrayFavProjects extends Component {
    setup () {
        this.orm = useService("orm");
        onWillStart(async () => {
            this.projects = await this.orm.searchRead(
                "project.project",
                ['|', ["stage_id.fold", "=", false], ["is_favorite", "=", true]],
                ["display_name", "is_favorite"]
            );
        });
    }
}
SystrayFavProjects.template = "project.SystrayFavProjects";
SystrayFavProjects.components = { SystrayFavProjectsItem, Dropdown };


export const systrayFavProjects = {
    Component: SystrayFavProjects
};
registry.category("systray").add("project.systray_fav_projects", systrayFavProjects, {sequence: 100});
