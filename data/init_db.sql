-----------------------------------------------------
-- users
-----------------------------------------------------

CREATE TABLE IF NOT EXISTS utilisateurs (
  id              SERIAL PRIMARY KEY,
  pseudo          TEXT UNIQUE NOT NULL,
  mot_de_passe    TEXT NOT NULL,
  cree_le         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-----------------------------------------------------
-- prompts
-----------------------------------------------------

CREATE TABLE IF NOT EXISTS prompts (
  id        SERIAL PRIMARY KEY,
  nom       TEXT UNIQUE NOT NULL,   -- ex: "fr_tutor_strict_v2"
  contenu   TEXT NOT NULL,
  version   INT NOT NULL DEFAULT 1,
  cree_le   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-----------------------------------------------------
-- conversations
-----------------------------------------------------

CREATE TABLE IF NOT EXISTS conversations (
  id          SERIAL PRIMARY KEY,
  titre       TEXT NOT NULL,
  prompt_id   INT NULL,  -- optionnel : la conversation peut être sans pré-prompt
  cree_le     TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  CONSTRAINT titre_non_vide CHECK (length(trim(titre)) > 0),
  CONSTRAINT fk_conversations_prompt
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE SET NULL
);

-----------------------------------------------------
-- conversations_participants
-----------------------------------------------------

CREATE TABLE IF NOT EXISTS conversations_participants (
  conversation_id  INT NOT NULL,
  utilisateur_id   INT NOT NULL,
  PRIMARY KEY (conversation_id, utilisateur_id),
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
  FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);

-----------------------------------------------------
-- Messages
-----------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
  id                SERIAL PRIMARY KEY,
  conversation_id   INT NOT NULL,
  utilisateur_id    INT NULL,                    -- NULL pour les messages "ia"
  emetteur          TEXT NOT NULL,               -- 'utilisateur' ou 'ia'
  contenu           TEXT NOT NULL,
  cree_le           TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Clés étrangères
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
  FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE SET NULL,

  -- L’émetteur doit être valide
  CONSTRAINT emetteur_check CHECK (emetteur IN ('utilisateur','ia')),

  -- Cohérence entre émetteur et utilisateur_id
  CONSTRAINT emetteur_utilisateur_match CHECK (
    (emetteur = 'ia' AND utilisateur_id IS NULL) OR
    (emetteur = 'utilisateur' AND utilisateur_id IS NOT NULL)
  ),

  -- Si utilisateur_id est renseigné, il doit être participant à la conversation
  FOREIGN KEY (conversation_id, utilisateur_id)
    REFERENCES conversations_participants(conversation_id, utilisateur_id)
    DEFERRABLE INITIALLY DEFERRED
);


-----------------------------------------------------
-- Index utiles 
-- (Permet de faire des lien directe entre les tables 
--  donc des recherches PLUS RAPIDE)
-----------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_messages_conv_cree
  ON messages (conversation_id, cree_le);

CREATE INDEX IF NOT EXISTS idx_participants_utilisateur
  ON conversations_participants (utilisateur_id);