

"charge des comptes analytiques par projet"
- possibilité de template
- sequence sur account_analytic_id pour retrouver tjs le même order sur les budgets
   par projets
- account_id par défaut selon la config produit / catégorie
- produit par défaut sur compte analytique

template / création par défaut :
- liste de template
- proposé par défaut : liste des template pré-remplis sur tous les projets, l'utilisateur peut les retirer
- si aucun proposé par défaut ou si tous retiré par l'utilisateur, dans tous les cas au moins
  1 budget vide sera créé par projet

#. Browse to *Accounting / Accounting / Account Move Budget / Budgets* and create
   a new budget sheet
#. Check *Template* and *Template (default)* boxes

#. Browse to *Project* app and create a new *Project*. Notice the *Budget templates*
   fields next to *Allocated Hours*, having previous budget suggested
#. Save the project. Notice the *Budget templates* field is now hidden. The *Budget*
   smart-button brings you to project's budget lines.

#. On any budget lines, *Details* button allow you to choose between 2 new valuation
   types. Select **Unit-Price**: budget debit and credit are computed via unit price
   and respective quantities
#. Selecting a *Product* allow to set a unit (and pre-fill unit price). Note that time
   unit are summed in *Allocated Hours* project field.
#. When choosing **Date-range**, unit-price is valued per time period, via product's
   variants. See *§Configuration*.
