from src.dao.db_connection import DBConnection


class PromptDAO:
    @staticmethod
    def get_id_by_name(nom: str) -> int | None:
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM prompts WHERE nom = %(nom)s;", {"nom": nom})
                row = cur.fetchone()
        return row["id"] if row else None

    @staticmethod
    def exists_id(prompt_id: int) -> bool:
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM prompts WHERE id = %(id)s;", {"id": prompt_id})
                return cur.fetchone() is not None

    @staticmethod
    def lister_prompts() -> list[dict]:
        """
        Renvoie la liste des prompts disponibles (id + nom), triés par id.
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
        Renvoie le texte du prompt correspondant à l'id donné.
        Essaie plusieurs noms de colonnes possibles pour le contenu.
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
