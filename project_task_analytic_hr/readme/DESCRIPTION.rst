
Natively, Task inherites their *Analytic Account* from their project.
This module adds *Analytic Account* field on HR Department and Employee forms,
and set default *Analytic Account* of tasks creating following the HR information
of the user who creates the task.

This can be useful, for instance in conjonction with modules `project_budget`
and `hr_timesheet`: project's Planned Hours can be splitted into several budgets,
and Timesheets on Tasks are automatically taken on those budget instead of general
project's budget.
