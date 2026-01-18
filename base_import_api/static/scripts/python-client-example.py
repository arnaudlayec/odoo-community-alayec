import xmlrpc.client
import ssl

class OdooClient:
    def __init__(self, url, db, username, password):
        """
        Initialise le client Odoo
        
        :param url: URL du serveur Odoo (ex: 'http://localhost:8069')
        :param db: Nom de la base de données
        :param username: Nom d'utilisateur
        :param password: Mot de passe
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        
        # Configuration SSL pour éviter les erreurs de certificat (dev uniquement)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        # Connexions aux services Odoo
        self.common = xmlrpc.client.ServerProxy(
            f'{url}/xmlrpc/2/common', 
            context=self.ssl_context
        )
        self.models = xmlrpc.client.ServerProxy(
            f'{url}/xmlrpc/2/object', 
            context=self.ssl_context
        )
    
    def authenticate(self):
        """
        Authentifie l'utilisateur et récupère l'UID
        
        :return: UID de l'utilisateur ou None si échec
        """
        try:
            self.uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
            if self.uid:
                print(f"Authentification réussie. UID: {self.uid}")
                return self.uid
            else:
                print("Échec de l'authentification")
                return None
        except Exception as e:
            print(f"Erreur d'authentification: {e}")
            return None
    
    def get_version(self):
        """
        Récupère la version d'Odoo
        
        :return: Informations de version
        """
        try:
            return self.common.version()
        except Exception as e:
            print(f"Erreur lors de la récupération de la version: {e}")
            return None
    
    def search(self, model, domain=None, limit=None, offset=0):
        """
        Recherche des enregistrements
        
        :param model: Nom du modèle (ex: 'res.partner')
        :param domain: Critères de recherche
        :param limit: Limite du nombre de résultats
        :param offset: Décalage pour la pagination
        :return: Liste des IDs trouvés
        """
        if not self.uid:
            print("Non authentifié")
            return []
        
        domain = domain or []
        kwargs = {'offset': offset}
        if limit:
            kwargs['limit'] = limit
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'search', [domain], kwargs
            )
        except Exception as e:
            print(f"Erreur de recherche: {e}")
            return []
    
    def read(self, model, ids, fields=None):
        """
        Lit des enregistrements
        
        :param model: Nom du modèle
        :param ids: Liste des IDs à lire
        :param fields: Liste des champs à récupérer
        :return: Liste des enregistrements
        """
        if not self.uid:
            print("Non authentifié")
            return []
        
        if not isinstance(ids, list):
            ids = [ids]
        
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'read', [ids], kwargs
            )
        except Exception as e:
            print(f"Erreur de lecture: {e}")
            return []
    
    def search_read(self, model, domain=None, fields=None, limit=None, offset=0):
        """
        Recherche et lit des enregistrements en une seule opération
        
        :param model: Nom du modèle
        :param domain: Critères de recherche
        :param fields: Liste des champs à récupérer
        :param limit: Limite du nombre de résultats
        :param offset: Décalage pour la pagination
        :return: Liste des enregistrements
        """
        if not self.uid:
            print("Non authentifié")
            return []
        
        domain = domain or []
        kwargs = {'offset': offset}
        if fields:
            kwargs['fields'] = fields
        if limit:
            kwargs['limit'] = limit
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'search_read', [domain], kwargs
            )
        except Exception as e:
            print(f"Erreur de search_read: {e}")
            return []
    
    def create(self, model, values):
        """
        Crée un nouvel enregistrement
        
        :param model: Nom du modèle
        :param values: Dictionnaire des valeurs
        :return: ID du nouvel enregistrement
        """
        if not self.uid:
            print("Non authentifié")
            return None
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'create', [values]
            )
        except Exception as e:
            print(f"Erreur de création: {e}")
            return None
    
    def write(self, model, ids, values):
        """
        Met à jour des enregistrements existants
        
        :param model: Nom du modèle
        :param ids: Liste des IDs à mettre à jour
        :param values: Dictionnaire des nouvelles valeurs
        :return: True si succès
        """
        if not self.uid:
            print("Non authentifié")
            return False
        
        if not isinstance(ids, list):
            ids = [ids]
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'write', [ids, values]
            )
        except Exception as e:
            print(f"Erreur de mise à jour: {e}")
            return False
    
    def unlink(self, model, ids):
        """
        Supprime des enregistrements
        
        :param model: Nom du modèle
        :param ids: Liste des IDs à supprimer
        :return: True si succès
        """
        if not self.uid:
            print("Non authentifié")
            return False
        
        if not isinstance(ids, list):
            ids = [ids]
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'unlink', [ids]
            )
        except Exception as e:
            print(f"Erreur de suppression: {e}")
            return False
    
    def get_fields(self, model):
        """
        Récupère la définition des champs d'un modèle
        
        :param model: Nom du modèle
        :return: Dictionnaire des champs
        """
        if not self.uid:
            print("Non authentifié")
            return {}
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'fields_get', [], {'attributes': ['string', 'help', 'type']}
            )
        except Exception as e:
            print(f"Erreur lors de la récupération des champs: {e}")
            return {}


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration de connexion
    URL="http://odoo-staging.asj.com"
    DATABASE="o18-flavigny-staging"
    USERNAME="4D@clairval.com"
    PASSWORD="36eefb487ae7649278e863d8799eecc350cff6e0"
    
    URL="http://localhost:8069"
    DATABASE="o18-flavigny"
    USERNAME="admin"
    PASSWORD="admin"
    
    # Création du client
    client = OdooClient(URL, DATABASE, USERNAME, PASSWORD)
    
    # Authentification
    if client.authenticate():
        # Affichage de la version
        version = client.get_version()
        print(f"Version Odoo: {version}")
        
        # Exemple 1: Lister les partenaires
        print("\n=== Partenaires ===")
        partners = client.search_read(
            'res.partner',
            domain=[('is_company', '=', True)],
            fields=['name', 'email', 'phone'],
            limit=5
        )
        for partner in partners:
            print(f"- {partner['name']} ({partner.get('email', 'N/A')})")
        
        # Exemple 2: Créer un nouveau partenaire
        print("\n=== Création d'un partenaire ===")
        new_partner_id = client.create('res.partner', {
            'name': 'Test Partner API',
            'email': 'test@example.com',
            'is_company': True,
            'phone': '+33123456789'
        })
        if new_partner_id:
            print(f"Nouveau partenaire créé avec l'ID: {new_partner_id}")
        
        # Exemple 3: Lire le partenaire créé
        if new_partner_id:
            partner_data = client.read('res.partner', new_partner_id)
            print(f"Données du partenaire: {partner_data}")
        
        # Exemple 4: Mettre à jour le partenaire
        if new_partner_id:
            success = client.write('res.partner', new_partner_id, {
                'phone': '+33987654321'
            })
            print(f"Mise à jour réussie: {success}")
        
        # Exemple 5: Récupérer les champs du modèle res.partner
        print("\n=== Champs du modèle res.partner ===")
        fields = client.get_fields('res.partner')
        for field_name, field_info in list(fields.items())[:5]:  # Affiche les 5 premiers
            print(f"- {field_name}: {field_info.get('string', '')} ({field_info.get('type', '')})")
    
    else:
        print("Impossible de se connecter à Odoo")
