
This module allow to manage project & tasks visibility through roles.
It fully relies on:
* existing and Odoo's native security access rules of project `Visibility`
* the `project_role` OCA module for project roles management and users assignments

This module also introduces a new security group `User (Global Reader)`, heriting
from project's User plus it reads all project & tasks indepently of its assignment
(like project's `Administrator`). 

In details, this module brings following changes.
Vocabulary note: a *Follower* is a partner subscribing to project's chatter.

#. Project's privacy default is changed to `followers` only, while Odoo's default
   `portal` let all projects be visible to all internal users. With `followers`,
   project's visibility is managed through followers list (Chatter subscribers).
   For more details, please read the project's form's tooltip (`Settings` tab).
#. A boolean field *Primary* is added on roles assignments, and 1 role can only have a single
   primary assignment per project.
#. All *Primary* users of a project are added and kept to its followers, so standard Odoo
   visibility project rules applies
#. A *Role* field is added on Project's *Stages* (`project.task.type`), allowing to assign
   by default all users of such role to any tasks moving to such state. This feature is inactive
   for all stages with no *Role* configured.

It also slightly adapts assignments views:
#. Menu-items: moves *Assignments* to *Configuration menu*
#. Project form: hides smart button *Assignments* and add *Assignments* in *Description*
   tab with Kanban layout

**Warnings:**

* This module largely takes control of project's *Followers* (though only for projects
  with `Visibility` on *followers*). You should not use it if you need to keep free
  or standar usage of Chatter's subscriptions.
* Even with project's `Visibility` set to *followers*, external partners can still
  subscribe to the project's chatter (i.e. partners with no user).
