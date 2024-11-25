
To use the features of this module:

#. Create a first new project (will be the parent one)
#. Start creating a second new project, and toggle the box "Is a sub-project?"
.. #. This replaces **Project name** field with **Parent project** field, that must be selected
#. Validate, and see the display name of the child project in the breadcrumbs like
   *"24-00001-01 - Parent's name"*

**Notes**

This module also adds constrains preventing:
- more than 2-level hierarchy for projects, ie. forbiding a child project to also
  become a parent itself.
- deleting parent projects with child(ren)
