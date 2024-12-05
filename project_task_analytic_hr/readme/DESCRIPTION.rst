
By default, Task inherites Analytic Account from their project.
This module changes this default behavior to set tasks' analytic account
based on HR department's or employee's default Analytic Account.

This can be useful, for instance in conjonction with modules `project_budget`
and `hr_timesheet`: project's Planned Hours can be splitted into several budgets,
and Timesheets on Tasks are automatically taken on those budget instead of general
project's budget.
