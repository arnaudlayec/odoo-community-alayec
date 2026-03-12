
This module is a *last-hope* solution for accountants that needs to reconcile
groupped bank statement lines, like daily groupped credit card transactions with
recent customer invoices, without any clue provided by the bank like:
* list of payments or invoices references honored by the groupped CB transaction
* list of the partners (of the same)

This module was designed for an e-commerce use-case where customers pay products by
credit card with the LCL French bank CB solution (Sherlock). Indeed, LCL does not
provide line-by-line transactions amounts but groups them with their own logics.

The algorithm works as follow:
1. it starts the day of the bank transaction
2. it looks for a combination of invoices/bills that matches the total amount of the
   transaction with a *Due date* on this date, in the limit of the *Maximum number
   of invoices/bills to look for* configured on the reconcile model. If tries to
   reconciliate a subset of invoices/bills or payments for which the sums of their
   total amounts exaclty matches the amount of the groupped transaction.
3. if the *Range of days* field is higher than 0, it starts included the invoice/bills
   the day before, the same day and the day after the transaction (+2 days in the research period)
4. it increases the searched period, day by day, in the limit of
   `1 + 2 * *Range of days*` days
