from psycopg2.extras import RealDictCursor

from src.dao.db_connection import DBConnection


class SessionDAO:
    """Accès table 'sessions' : ouvre/ferme une session utilisateur."""

    def ouvrir(self, user_id: int, device: str | None = "cli") -> int:
        """Crée une ligne (connexion=NOW()) et renvoie l'id de session BDD."""
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
        """Pose deconnexion=NOW() sur la dernière session encore ouverte (s'il y en a une)."""
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE sessions
                       SET deconnexion = NOW()
                     WHERE user_id = %(uid)s
                       AND deconnexion IS NULL
                     ORDER BY connexion DESC
                     LIMIT 1;
                    """,
                    {"uid": user_id},
                )
                return cur.rowcount > 0
