
1. Browse to Invoicing / Settings / Reconciliation Models and create a new model
2. Select the new type *"Rule to match invoices/bills (combo)"*
   It is similar to *"Rule to match invoices/bills"* but wil not use
   either the statement name or the partner. It will look back in the
   past days to find a combination of invoices that matches the total amount
   of the transaction.
3. Configure the settings like rules of type *Rule to match invoices/bills*, except:
   * the *Range of days* instead of *Past months*:
      * 0 means the invoices/bills search is limited to the date of the transaction
        (based on the *Due date* of the invoices/bills)
      * 1 means +1 and -1 days around the transaction date
   * the *Maximum number of invoices/bills to look for* (empty means infinite)

It is strongly advise to order this rule in the last ones, and to keep it without
*Automated validation* checked.
