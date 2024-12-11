
#. Browse to *Accounting / Accounting / Account Move Budgets / Budget lines templates*
#. Create a line with a *General Account*, *Analytic Account* filled in
#. You may create other template lines, and order by priority. Only first line matching
   the the search pattern (*) will be used
#. In a budget, create a new line and select an Analytic Account. The *General Account* fills
   in automatically
#. Any value changes of *General Account*, *Analytic Account* or *Partner* will trigger an
   attempt to fill in empty fields of the line


(*) Search pattern is as follow:
* when *creating* a line or *changing* a line value...
* ...of the *search keys* having a value, search template entries matching all those values
* take the 1st matching template line
* set any of the empty field of the real budget line, if there is any and if possible
