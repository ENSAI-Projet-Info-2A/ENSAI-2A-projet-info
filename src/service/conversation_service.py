from typing import List
from conversation import Conversation
from echange import Echange
from datetime import datetime as Date


class ConversationService:

    def creer(self, titre: str, personnalisation: str) -> Conversation:
        pass

    def acceder(self, id_conv: int) -> Conversation:
        pass

    def renommer_conv(self, id_conv: int, nouveau_nom: str) -> bool:
        pass

    def supprimer_conv(self, id_conv: int) -> bool:
        pass

    def lister_conv(self, id_user: int) -> List[Conversation]:
        pass

    def rechercher_conv(self, id_user: int, motcle: str, date: Date) -> List[Conversation]:
        pass

    def lire_fil(self, id_conv: int, offset: int, limit: int) -> List[Echange]:
        pass

    def rechercher_message(self, id_conv: int, motcle: str, date: Date) -> List[Echange]:
        pass

    def ajouter_utilisateur(self, id_conv: int, id_user: int, role: str) -> bool:
        pass

    def retirer_utilisateur(self, id_conv: int, id_user: int) -> bool:
        pass

    def mettre_a_jour_personnalisation(self, id_conv: int, personnalisation: str) -> bool:
        pass

    def exporter_conversation(self, id_conv: int, format: str) -> bool:
        pass

    def demander_assistant(self, message: str, options=None) -> Echange:
        pass