```mermaid

erDiagram
    UTILISATEURS ||--o{ CONVERSATIONS : "propriétaire"
    UTILISATEURS ||--o{ CONVERSATIONS_PARTICIPANTS : "participe"
    UTILISATEURS ||--o{ MESSAGES : "envoie"
    UTILISATEURS ||--o{ SESSIONS : "a"
    PROMPTS ||--o{ CONVERSATIONS : "initialise"
    CONVERSATIONS ||--o{ MESSAGES : "contient"
    CONVERSATIONS ||--o{ CONVERSATIONS_PARTICIPANTS : "associe"

    UTILISATEURS {
        int id PK
        string pseudo UK
        string mot_de_passe
        time temps_utilisation
        timestamptz cree_le
    }

    PROMPTS {
        int id PK
        string nom UK
        text contenu
        int version
    }

    CONVERSATIONS {
        int id PK
        string titre
        int proprietaire_id FK "nullable"
        int prompt_id FK "nullable"
        timestamptz cree_le
    }

    CONVERSATIONS_PARTICIPANTS {
        int conversation_id PK,FK
        int utilisateur_id PK,FK
    }

    MESSAGES {
        int id PK
        int conversation_id FK
        int utilisateur_id FK "nullable"
        string emetteur "utilisateur|ia"
        text contenu
        timestamptz cree_le
    }

    SESSIONS {
        int id PK
        int user_id FK
        timestamptz connexion
        timestamptz deconnexion "nullable"
    }