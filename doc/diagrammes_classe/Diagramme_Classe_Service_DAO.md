---
config:
  flowchart:
    curve: basis
---
classDiagram
direction TB
    class Utilisateur_Service {
	    +creer_compte(pseudo: string, mdp: string) : Utilisateur
	    +trouver_par_id(id: int) :utilisateur
	    +trouver_par_pseudo(pseudo: string) : Utilisateur
	    +lister_tous() : list~Utilisateur~
	    +supprimer(user_id: int) : bool
	    +pseudo_deja_utilise(self, pseudo: str) :bool
    }

    class Auth_Service {
	    +se_connecter(pseudo: string, mdp: string) : string %% retourne token/sessionId
	    +se_deconnecter(token: string) : void
	    +verifier_token(token: string) : bool
    }

    class Conversation_Service {
	    +creer_conv(titre: string, personnalisation: string, id_proprietaire: int) : Conversation
	    +acceder_conv(id_conv: int) : Conversation
	    +renommer_conv(id_conv: int, nouveau_nom: string) : bool
	    +supprimer_conv(id_conv: int) : bool
	    +lister_conv(id_user: int) : List~Conversation~
	    +rechercher_conv(id_user: int, motcle: string, date: date) : List~Conversation~
	    +lire_fil(id_conv: int, offset: int, limit: int) : List~Echange~
	    +rechercher_message(id_conv: int, motcle: string, date: date) : List~Echange~
	    +demander_assistant(id_conv: int, temperature: double, top_p: double, max_tokens: int, stop: List) : Echange  %% crée échange assistant
	    +ajouter_utilisateur(id_conv: int, id_user: int, role: string) : bool
	    +retirer_utilisateur(id_conv: int, id_user: int) : bool
	    +mettre_a_jour_personnalisation(id_conv: int, personnalisation: string) : bool
	    +exporter_conversation(id_conv: int, format: string="json") : string
    }

    class Statistiques_Service {
	    +stats_utilisateur(id_user: int) : Statistiques
    }

    class Utilisateur_DAO {
	    +creer_utilisateur(pseudo: string, password_hash: string) : Utilisateur
	    +trouver_par_id(id: int) : Utilisateur
	    +trouver_par_pseudo(pseudo: string) : Utilisateur
	    +lister_tous() : list[Utilisateur]
	    +supprimer(id: int) : bool
	    +heures_utilisation(user_id: int) :float
	    +heures_utilisation_incl_courante(user_id: int) : float
    }

    class Conversation_DAO {
	    +creer_conv(titre: string, personnalisation: string, owner_id: int) : Conversation
	    +est_proprietaire(conversation_id: int, utilisateur_id: int) :bool
	    +trouver_par_id(id_conv: int) : Conversation
	    +renommer_conv(id_conv: int, nouveau_nom: string) : bool
	    +supprimer_conv(id_conv: int) : bool
	    +lister_conversations(id_user: int) : List~Conversation~
	    +rechercher_mot_clef(id_user: int, motcle: string) : List~Conversation~
	    +rechercher_date(id_user: int, date: date) : List~Conversation~
	    +rechercher_conv_motC_et_date(id_user: int, mot_cle: str, date: datetime.date) :List~Conversation~
	    +lire_echanges(id_conv: int, offset: int, limit: int) : List~Echange~
	    +rechercher_echange(id_conv: int, motcle: string, date: date) : List~Echange~
	    +ajouter_participant(id_conv: int, id_user: int, role: string) : bool
	    +retirer_participant(id_conv: int, id_user: int) : bool
	    +ajouter_echange(id_conv: int, e: Echange) : bool
	    +mettre_a_jour_personnalisation(id_conv: int, personnalisation: string) : bool
	    +compter_conversations(id_user: int) : int
	    +compter_messages_user(id_user: int) : int
	    +sujets_plus_frequents(id_user: int, topK: int) : list~string~
	    +mettre_a_j_preprompt_id(conversation_id: int, prompt_id: int) : bool
    }

    class LLM_API {
	    +generate(history: List~Echange~, temperature: double, top_p: double, max_tokens: int, stop: List) : Echange
    }

    class PromptDAO {
	    +get_id_by_name(nom: str) :int | None
	    +exists_id(prompt_id: int) : bool
	    +lister_prompts() :list[dict]
	    +get_prompt_text_by_id(prompt_id: int) :str
    }

    class sessionDAO {
	    +ouvrir(self, user_id: int, device: str | None = "cli") :int
	    +fermer_derniere_ouverte(self, user_id: int) :bool
    }

    Statistiques_Service ..> Utilisateur_DAO : "appelle"
    Utilisateur_Service ..> Utilisateur_DAO : "appelle"
    Auth_Service ..> Utilisateur_DAO : "appelle"
    Conversation_Service ..> Conversation_DAO : "appelle"
    Conversation_Service ..> PromptDAO : "appelle"
    Conversation_Service ..> LLM_API : "appelle"
    Statistiques_Service ..> Conversation_DAO : "agrégations"