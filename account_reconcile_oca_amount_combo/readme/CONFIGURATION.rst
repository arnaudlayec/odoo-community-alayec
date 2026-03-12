
1. Browse to Accounting / Settings / Reconciliation Models and create a new
   reconciliation model
2. Select the type *"Rule to match invoices/bills"* and activate the
   new field *Combo amount-mode*
3. Configure the settings like a standard rule of this type, except:
   * the *Range of days* instead of *Past months*:
      * 0 means the invoices/bills search is limited to the date of the transaction
        (based on the *Due date* of the invoices/bills)
      * 1 means +1 and -1 days around the transaction date
   * the *Maximum number of invoices/bills to look for* (empty means infinite)

It is strongly advise to:
* order this rule as the last one
* keep it without *Automated validation* checked
* set the new fields *Range of days* and *Maximum number of invoices/bills*
