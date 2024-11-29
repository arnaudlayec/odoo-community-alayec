
This module introduces 3 features.
The first 2 are ready-to-use, while the 3rd is for developers.


1. Top-screen project dropdown menu
************************************

Very similarly than company switch, this module adds a dropdown menu on top-right corner
of all Odoo's screens, next to user name, activities and chatter buttons, allowing to select
one's favorite projects.

This is useful for some businesses where employees works several hours or days, on the same
project(s). This module alone have little interest, but when combined with default filters on
wanted views, it allows end-users to be freed of the pain to filter themselves on their
working project(s) - see "§ Configuration".

Note: this is an alternative to new project-bar of Odoo 18.0.


2. Synchronization between project's followers and user's favorites project
****************************************************************************

This module detect addition / removal of internal users in a project's chatter followers list
and pushes the action to add / remove the project from user's favorite.
This is especially useful in combination with `project_role_visibility` when a project's followers
list is itself populated with user assignments on project's roles.


3. Project-choice wizard, before opening an action
***************************************************

This module also provides a ready-to-use (in code) wizzard that may be called from a server action
and will return a new action filtered on a specific project.

This is very useful for views which are not relevant when not filtered 1st on specific projects, while
offering an acceptable user-experience of project choice before accessing their view.
Technically, it only return action dict from existing actions with added context key(s) like
`default_project_id` and domain part like `[('project_id', '=', id)]`.

Example is given in `wizard/project_choice_example.xml`.
See method `action_choose_project_and_redirect()` in model `project.choice.wizard` for more information.
