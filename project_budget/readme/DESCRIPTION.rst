
This module extends project's budget management capacity by relying on
other OCA module **Account Budget Move**, aiming to offer the possibility
of managing more than one budget and budget lines per project where Odoo
CE allows single field *Allocated Hours*.

Mainly, it adds:

* a *Project* field on Budget sheet and a *Budget* smart-button on project
  form
* capacity to manage Budget sheet template, that can be *selectable* or
  *pre-selected* at project creation (if none selected, an empty budget
  sheet with no lines will always be created)
* type on budget lines, allowing to value the amount (in currency) of the
  line with 2 methods (per quantity and unit price, and per quantity and
  date-ranged unit price)
* a *Default Product Template* field on *Analytic Account*, allowing to
  fasten budget fill-in for the new introduced budget line valuation type
  (e.g. pre-filled unit price)


This module was though to depend on `hr_timesheet` though the dependance
is not strong (i.e. mainly the automated computation of *Allocated Hours*
field).
