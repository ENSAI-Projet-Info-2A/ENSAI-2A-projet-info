from src.business_object.echange import Echange
from src.client.llm_client import LLM_API


def main():
    # On crée une instance du client
    api = LLM_API()

    # On crée un petit historique de conversation
    history = [
        Echange(agent="system", message="Tu es un assistant utile."),
        Echange(
            agent="user",
            message="Bonjour, peux-tu me donner une recette de cookies au chocolat ?",
        ),
    ]

    # On appele la méthode generate()
    print("Envoi de la requête au modèle…")
    reponse = api.generate(history=history, temperature=0.7, top_p=1.0, max_tokens=150)

    # On vérifie le résultat
    print("\n Réponse :")
    print("Agent :", reponse.agent)
    print("Nom   :", reponse.agent_name)
    print("Texte :", reponse.message)


if __name__ == "__main__":
    main()
