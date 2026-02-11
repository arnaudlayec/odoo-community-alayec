
- page module
  - données démo
  - v18.0
  - assez simple qui :
    > se base sur les modules d'import de factures déjà existants
    > utilise l'API native de Odoo (XML-RPC) : va disparaitre en v20 (septembre 2026) -> api "JSON-2 API"
    > enrichi pour gérer des imports de commandes e-commerce en factures dans Odoo
      => création auto des contacts
      => gestion addresses de facturation et livraison
      => validation des factures à la volée quand possible
    > interface de suivi des imports (besoin de contrôle)

- compte technique 4D
  - 2 niveaux d'accès
  - utilisateur (vérification)
  - manager (rejouer l'import, altérer la donner, revenir en arrière)
    > manipulation "dangereuse" plutôt pour du débuggage dans un environnement de test
    > niveau requis pour le compte technique

- montrer écran avec jeux de données démo
  - niveau "admin" : toucher/comprendre la configuration
  - et la données
  - expliquer les status des lignes et du rapport
    - ligne à ligne : "Vérifié/non vérifie"
    - all in sur le rapport : "marquer comme tout vérifier"
  - expliquer le rapport (dynamique)
  - expliquer boutons du haut :
    > enregistrements créés (du modèle) => n'affiche pas les partenaires et paiements
      + pointent aussi les possibles "doublons" (external ref). Ex : 2 imports de factures en brouillon
  - expliquer notification (+ config user mail/notif Odoo)
    => reçoivent le rapport synthétique

- exemple réel
  - position fiscale
  - addresse de livraison
  - différence de montant
  - journal de vente différent -> nom de la facture
  - produits : reconnus -> permet de définir taxes et comptes (selon positions fiscale)
    > aussi possible sans produit (module de base)
    > Pour compta B2C : était préférable de garder la main "par Odoo" sur comptes et taxes
  - paiements : validés. En attente Rappro bancaire
