
The only configuration is the format of the template sequence for the child projects.
By default, it is simply configure to a 2-digits incremental sequence with suffix **"-"**.
To change it, modify the **archived** sequence named *Child Project sequence*.
This sequence is copied per-project when a child project is linked to a (newly)-parent project,
and suffix of the instanciated sequence is itself suffixed with the `parent_id.sequence_code`.

The `display_name` format of both parent and child project keeps the format configuration of
`project_parent` module in Global Parameters, like: *1234-01 - Project name*
