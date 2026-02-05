

déplacer l'interface au niveaux des commandes plutôt que des factures clients.

- prérequis : import en masse des articles
- matching mais pas d'import auto des articles
- gérer les commandes qui pourraient tomber en échec d'import dans Odoo (ref produit inconnue)
  (Les commandes avec des références d'articles inconnus de Odoo ne seront pas importés et un signalement sera effectué)

- seules les commandes payées continueront d'être importées.
- créer des "commandes clients" est la création puis gestion des envois des commandes VPC depuis Odoo (une commande client génère automatiquement une "livraison à effectuer" en lien avec la commande).
    option "création de livraison" pour "éteindre" les stock.picking

    option "auto_create_invoice" à False pour Flavigny
