from psycopg2.extras import RealDictCursor

from src.dao.db_connection import DBConnection


class SessionDAO:
    """
    Data Access Object (DAO) pour la gestion des sessions utilisateurs.

    Cette classe interagit avec la table ``sessions`` et permet
    d'ouvrir et de fermer les sessions d’un utilisateur.
    Elle représente une couche d'accès simple et directe à la base de
    données, sans logique métier supplémentaire.

    Table concernée
    ----------------
    Table : ``sessions``
    Colonnes utilisées :
    - ``id`` (int) : identifiant unique de la session
    - ``user_id`` (int) : identifiant de l'utilisateur concerné
    - ``connexion`` (timestamp) : date et heure de début de session
    - ``deconnexion`` (timestamp, nullable) : date de fin de session
    """

    def ouvrir(self, user_id: int, device: str | None = "cli") -> int:
        """
        Ouvre une nouvelle session pour un utilisateur.

        Insère une nouvelle ligne dans la table ``sessions`` avec :
        - ``connexion = NOW()``
        - ``deconnexion = NULL``
        La session est donc considérée comme ouverte.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur qui se connecte.
        device : str, optional
            Type d'appareil ou contexte de connexion (non utilisé dans la requête
            mais laissé pour extensions futures). Par défaut "cli".

        Returns
        -------
        int
            L'identifiant de la session nouvellement créée.
        """
        with DBConnection().connection as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO sessions(user_id, connexion, deconnexion)
                    VALUES (%(uid)s, NOW(), NULL)
                    RETURNING id;
                    """,
                    {"uid": user_id},
                )
                row = cur.fetchone()
                return int(row["id"])

    def fermer_derniere_ouverte(self, user_id: int) -> bool:
        """
        Ferme la dernière session encore ouverte de l'utilisateur.

        Met à jour la session la plus récente ayant :
        - ``user_id = user_id``
        - ``deconnexion IS NULL``
        en posant ``deconnexion = NOW()``.

        S'il n'existe aucune session ouverte pour cet utilisateur, rien n'est modifié.

        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur dont on veut fermer la session active.

        Returns
        -------
        bool
            True si une session a été trouvée et fermée,
            False sinon.
        """
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE sessions
                    SET deconnexion = NOW()
                    WHERE id = (
                        SELECT id
                        FROM sessions
                        WHERE user_id = %(uid)s
                        AND deconnexion IS NULL
                        ORDER BY connexion DESC
                        LIMIT 1
                    );
                    """,
                    {"uid": user_id},
                )
                return cur.rowcount > 0
