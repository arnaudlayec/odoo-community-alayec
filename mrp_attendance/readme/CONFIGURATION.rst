
In global *Settings*
====================
#. *Manufacturing*: enable *Work Orders*
#. *Attendance*: this module fully use the default *Attendance* settings (Barcode, PIN, manual selection)

User Rights
===========

>>>> a ré-écrire 
Ajout de 2 groupes:
- Manufacturing Workers : requis sur le **User**, configuration qui distingue des autres employés. Peut être utilisé pour le compte partagé si PIN configuré.
- Manufacturing Officers : ne gère que les précédents ; requis pour le compte partagé si bypass du PIN.


User Rights *Manufacturing Workers*:
#. Create 1 user per employee requiring to log *Manufacturing Times*. This is important: even if *Attendance*
   application only requires Employees, this module requires Users because Manufacturing *Productivity* records
   is based on Users.
#. Add them to the Group: *Attendance / Manufacturing Worker*. This group:
     * limits to see only other *Manufacturing Workers* in the *Attendance* app
     * discrepencies in *Attendance* app which Employee redirects to *Manufacturing Times* instead
       of native Check IN / Check OUT

Shared user for Kiosk mode on Warehouse computers (recommanded but optional):
#. Create a new Odoo technical/shared account (advice: configured double-authentication with a phone staying on
   the warehouse)
#. From the tab *Preferences* in User form, configure the default home action to *Manufacturing Times*
#. Add this user to the group *Attendance / Manufacturing Worker* but don't create any Employee
#. Log with this account from the warehouse computers
