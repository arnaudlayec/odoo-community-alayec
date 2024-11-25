
This module makes a bridge between `project_parent` and `project_sequence`
in order to replace common project's sequence by a per-parent sequence to generated
`sequence_code` of child projects. This allows displaying child projects with
`sequence_code` like `1234-01` where `1234` is parent's code and `01` the child's code.

.. Futhermore, if parent's project `name` is defined (i.e. set by user different to
.. `sequence_code`) the children project's name is forced to its parent's name.
.. This allows rendering the `display_name` of child projects like:
.. `1234-01 - Parent's project`

On user-experience side, it adds a toggle `child_project` only shown at project creation.
This helps showing `parent_id` field only when toggled (and vice-versa).
