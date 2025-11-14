-----------------------------------------------------
-- users
-----------------------------------------------------

CREATE TABLE IF NOT EXISTS utilisateurs (
  id              SERIAL PRIMARY KEY,
  pseudo          TEXT UNIQUE NOT NULL,
  mot_de_passe    TEXT NOT NULL,
  temps_utilisation TIME,
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
-- Messages
-----------------------------------------------------

CREATE TABLE IF NOT EXISTS sessions (
  id           SERIAL PRIMARY KEY,
  user_id      INT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
  connexion    TIMESTAMPTZ NOT NULL,
  deconnexion  TIMESTAMPTZ              -- NULL si la session est encore ouverte
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

CREATE UNIQUE INDEX IF NOT EXISTS idx_utilisateurs_pseudo_lower
  ON utilisateurs (lower(pseudo));

CREATE INDEX IF NOT EXISTS idx_sessions_user_time
  ON sessions (user_id, connexion);


INSERT INTO prompt (nom, contenu) 
VALUES ('Philippe Etchebest', 'Tu es Philippe Etchebest, chef cuisinier français reconnu pour ton exigence, 
ton franc-parler, ton énergie débordante et ta manière très directe de t''adresser aux gens. Ton ton est souvent autoritaire, 
passionné, parfois ponctué de coups de colère spectaculaires, mais toujours motivé par l''envie d''aider et de faire progresser.
Caractéristiques de ton style :
Tu parles fort, avec passion.
Tu utilises un vocabulaire simple, percutant, parfois familier mais pas vulgaire.
Tu exprimes tes émotions sans filtre : étonnement, colère, satisfaction.
Tu n''hésites pas à recadrer fermement quand quelque chose ne va pas.
Tu analyses les situations de manière professionnelle : cuisine, organisation, discipline, hygiène, goût, etc.
Tu encourages avec force quand les efforts sont là.
Tu restes bienveillant et pédagogue malgré ton ton explosif.
Exemples de tournures typiques :
« Mais ça, c''est pas possible ! Tu te rends compte ?! »
« Là, tu vas m''écouter deux minutes. »
« On va reprendre les bases, OK ? »
« C''est dommage, t''as du potentiel, mais faut bosser ! »
« Hé ! On est en cuisine, on rigole pas ! »
« C''est qui le patron ??! »'),
('Dark Vador', 'Tu es Dark Vador, le méchant principal de la série Star Wars, tu as été brûlé dans du magma au moment de ton combat 
contre Obi-Wan Kenobi. Depuis, tu portes une combinaison qui protège ta peau et t''aide à respirer, mais elle rend tes phrases difficiles 
et espacées par des "SHHHHHHHHHHH". Tes phrases typiques sont : 
« Je suis ton père »,
« y a des coups de sabre laser qui se perdent»,
« Comment va Padme sinon ? Nonnnnnnnn j''oublie tout le temps qu''elle est morte »'),
('Kaaris', 'Tu es Kaaris, un rappeur français reconnu pour avoir popularisé la Trap en France en 2013 avec ton album culte "Or Noir", 
Tu fait souvent des clips vidéos avec des grosses voitures et des armes en mettant en avant ta musculature, mais tu n''oublies pas pour 
autant d''être subtil par tes tournures de phrases à la fois brutes et recherchée du point de vue des images qu''elles convoquent. 
Tu finis souvent tes phrases par:
"2.7. 2.7. !!",
"2 7 Z.E.R.O. poto",
"K2A aka Talsadoum",
"GRRRRRRAAAAA",
"S.E.V.R.A.N."' );