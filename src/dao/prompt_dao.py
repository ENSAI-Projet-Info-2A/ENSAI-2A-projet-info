from dao.db_connection import DBConnection


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
