
This very simple module simplifies standard Odoo feature by making *Task Stages*
common and shared between all projects.
It becomes possible for HR department managers to review and plan their employee's
tasks (daily, weekly, monthly, ...) for all projects at once and for employee to
view and follow this planification by their manager without sub-layer of personnal
stages. For project managers, they may still rely on tasks *Objective date* to
request a deadline, and see on task *Stage* when the team committed to realize the
task.

This is convenient for companies where task stages is the same for all projects
**and** do not have many employees working on the same tasks (since personal
stages are made **unavailable**).

Technically, this module:
* replaces the grouping per *Personal Stages* in `My Tasks` view by a grouping per
  standard *Task Stages* and hides any *Personal Stages* in Kanban column
* make all *Task Stages* common to all *Projects*, i.e. *Task Stages* are not managed
  per-project anymore
* loads by default the following common-to-all-projects *Task Stages* (similarly than)
  native *Personal Stages*:

    * Incoming (not planned)
    * Today
    * This week
    * Next week
    * This month
    * Next month
    * Later

Note: due to deep implementation of personal stage in Odoo CE code, a small part of the
feature remains available. When creating a *Private* Task (with no project), it it shown
in a left column *None* in Kanban view, until the task is affected to a Project.
