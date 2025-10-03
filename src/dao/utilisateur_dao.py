class Utilisateur_DAO:

    def créer_utilisateur(pseudo: string, password_hash: string) : Utilisateur
        pass

    def get_par_id(id: int) : Utilisateur
        pass

    def trouver_par_pseudo(pseudo: string) : Utilisateur
        pass

    def supprimer(id: int) : bool
        pass

    def get_hash_par_pseudo(pseudo: string) : string
        pass