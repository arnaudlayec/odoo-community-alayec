
Some businesses having quite *big* Manufacturing Orders taking much time,
like Construction, might need to consider the components of their MOs as
*out* of their inventory *without waiting for* the full validation
of their MOs.

This module:
* decrease product's *Available quantity* (i.e. `stock.quant`.`quantity`)
  with *Consumed* components quantity even for MOs in *In Progress* state
* display a *Preparation status* of the MO, that can be forced (like the *Confirm*
  button on pickings)



==========
NOTES / DRAFT
==========

Changement méthode calcul niveau de stock :
    Update du stock_quant dès write() ou create() d'un composant, /!\ dans le write(), travailler en écart de la valeur précédente
    Re-calcul des stock.quant rétroactif à l'install du modèle
    Re-calcul ... à l'uninstall
    /!\ validation du MO ?
