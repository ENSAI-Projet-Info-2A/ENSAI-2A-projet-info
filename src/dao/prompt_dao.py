from src.dao.db_connection import DBConnection


class PromptDAO:
    """
    Data Access Object (DAO) pour les prompts stockés en base de données.

    Cette classe fournit un ensemble de méthodes statiques permettant
    d'interroger la table ``prompts`` : récupération d'identifiants,
    vérification d'existence, obtention du texte d'un prompt et liste
    des prompts disponibles.

    Toutes les méthodes ouvrent une connexion via ``DBConnection`` et
    utilisent des curseurs contextuels pour garantir la fermeture
    correcte des ressources.

    Table concernée
    ----------------
    Table : ``prompts``  
    Colonnes utilisées :
    - ``id`` (int)
    - ``nom`` (str)
    - ``contenu`` (str) — peut avoir d'autres variantes selon la structure interne
    """
    @staticmethod
    def get_id_by_name(nom: str) -> int | None:
        """
        Retourne l'identifiant d'un prompt à partir de son nom.

        Parameters
        ----------
        nom : str
            Nom exact du prompt à rechercher.

        Returns
        -------
        int | None
            L'identifiant du prompt si trouvé, sinon ``None``.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM prompts WHERE nom = %(nom)s;", {"nom": nom})
                row = cur.fetchone()
        return row["id"] if row else None

    @staticmethod
    def exists_id(prompt_id: int) -> bool:
        """
        Vérifie si un prompt existe en base à partir de son identifiant.

        Parameters
        ----------
        prompt_id : int
            Identifiant du prompt.

        Returns
        -------
        bool
            True si le prompt existe, False sinon.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM prompts WHERE id = %(id)s;", {"id": prompt_id})
                return cur.fetchone() is not None

    @staticmethod
    def lister_prompts() -> list[dict]:
        """
        Renvoie la liste des prompts disponibles.

        Les résultats sont triés par identifiant et retournés sous forme
        de dictionnaires (ex. ``{"id": 1, "nom": "Prompt X"}``).

        Returns
        -------
        list[dict]
            Liste complète des prompts présents en base.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, nom
                    FROM prompts
                    ORDER BY id;
                    """
                )
                rows = cur.fetchall() or []
        return rows

    @staticmethod
    def get_prompt_text_by_id(prompt_id: int) -> str | None:
        """
        Renvoie le texte d'un prompt à partir de son identifiant.

        La méthode récupère toute la ligne de la table puis tente d'extraire
        le contenu du champ ``contenu`` (ou autre champ éventuel si la table
        évolue). Si aucun enregistrement n'est trouvé, elle renvoie ``None``.

        Parameters
        ----------
        prompt_id : int
            Identifiant du prompt recherché.

        Returns
        -------
        str | None
            Le texte du prompt, ou ``None`` s'il n'existe pas en base.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM prompts
                    WHERE id = %(id)s;
                    """,
                    {"id": prompt_id},
                )
                row = cur.fetchone()

        if not row:
            return None

        # row est un dict-like (RealDictRow)
        texte = row.get("contenu")
        return texte or None
