
Odoo 16.0 attendance workflow (legacy JS):

1. *hr_attendance_action_kiosk_mode*: action clients called from kiosk mode menu
    > triggers Js tag *hr_attendance_kiosk_mode*
2. js action_registry *hr_attendance_kiosk_mode*
    > calls action *hr_attendance.hr_employee_attendance_action_kanban* on 'Identify manually' button click
    *or*
    > calls *_rpc* hr.employee/attendance_scan() on scan
    [END] redirects to `_attendance_action` with **next_action: hr_attendance.hr_attendance_action_kiosk_mode**


[END] *_attendance_action* with *next_action*
**My Attendances**
    1+3. (1) "Mitchel Admin / Welcome [Check IN]" or (3) "Mitchel Admin / Want to checkout? Today's work hours: xx:yy:zz [Check OUT]"
    2. Check in -> "Welcome + Good morning + Checked in at xx:yy:zz" + [OK] or timer --> 3.
    4. Check out -> Have a good day > checkout at ?... extra hours ... > [Goodbye] or timer --> 1.
**Kiosk mode**
    1. Scan badge or 'identifiy manually'
    2. Check in > ok --> **Kiosk mode**
