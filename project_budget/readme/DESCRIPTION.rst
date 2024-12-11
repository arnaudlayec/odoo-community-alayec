
This module extends project's budget management capacity, by relying on
other OCA module **Account Budget Move**. It allows managing more than one budget
and budget lines per project, for Goods or Times, where Odoo CE has a single
field per project *Allocated Hours*.
This is useful for very large project mixing time and goods, for instance in
construction business-line.

Mainly, it adds:

* a *Project* field on Budget sheet and a *Budget* smart-button on project
  form
* capacity to manage Budget sheet template, that can be *selectable* or
  *pre-selected* at project creation (if none selected, an empty budget
  sheet with no lines will always be created)
* type on budget lines, allowing to value line with amount in currency (original
  feature) or per quantity and unit price


It remains fully possible to use budget and budget lines for non-project budgets.


Few module can extend this one, in the aim to load budget to Analytic Account and
use analytics to follow budget consumption:

* `projet_budget_line_template`: fasten budget line filling (e.g. avoiding project
  managers to fill in General Accounting field)
* `project_budget_timesheet`: computes project's field *Allocated Hours* from
  budget identified as timesheetable, and limits tasks *Planned Hours* to available
  budget per analytic account. Analytic Account on tasks is guessed is per HR
  settings introduced by dependant module `project_task_analytic_hr`
* `project_budget_workforce`: adds 3rd line type *Workforce* to value budget line
  with a unit price varying per date ranges (re-using modules `hr_employee_cost_history`
  and `hr_department_cost_history`)
