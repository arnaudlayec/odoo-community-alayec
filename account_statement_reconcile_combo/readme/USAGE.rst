
The algorithm works as follow:
1. it starts the day of the bank transaction
2. it looks for a combination of invoices/bills that matches the total amount of the
   transaction with a *Due date* on this date, in the limit of the *Maximum number
   of invoices/bills to look for* configured on the reconcile model.
3. if the *Range of days* of higher than 0, it starts looking invoices for
   invoices/bills the day before, the same day and the day after the transaction
4. etcetera, in the limit of `1 + 2 * *Range of days*` days
