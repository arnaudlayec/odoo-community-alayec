
**Default filters can be set on views by different ways:**
#. By Administrator, from *Settings / Technical / §User-interface / User-defined Filters*
#. By end-user
#. By custom code

**Example of 1.:**
* *Filter name*: name of default filter that all users will see
* *Available for User*: keep empty so it applies to all users
* *Model*: choose the right model corresponding to your view
* *Default Filter*: yes, so its applies by default at view load
* *Action*: action that loads the view you want the filter to apply. To retrieve it:
    #. Activate debug mode
    #. Browse to the view
    #. In debug menu, open *Edit Action*
    #. Retrive the 1st field `Action Name`
* *Active*: yes
* *Domain*: see below
* *Context* and *Sort*: you might need to configure them to reproduce any default filter
  that could already be active on your view

**Example of domain for filtering a model by favorite projects (for 1. and 3.):**

.. code-block:: python
    
    [('project_id.favorite_user_ids','=',uid)]

Or XML code to add to a **<search>** view:

.. code-block:: XML

    <filter string="★ Projects"
        name="my_favorite_projects"
        domain="[('project_id.favorite_user_ids','=',uid)]"
    />

with following context arg in the action loading the view:

.. code-block:: python

    {'my_favorite_projects': 1}


**Technical field `res_users.favorite_project_id`**
Also, this module provides `favorite_project_id` field on `res_users` (computed, store).
This allow for instance to add a `project_id` field on any domain and fill it in by default:
 
.. code-block:: python

    project_id = fields.Many2one(
        'project.project',
        'Project',
        default=lambda self: self.env.user.favorite_project_id
    )
