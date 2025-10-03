-----------------------------------------------------
-- Joueur
-----------------------------------------------------

-- DROP TABLE IF EXISTS joueur CASCADE ;
-- CREATE TABLE joueur(
--     id_joueur    SERIAL PRIMARY KEY,
--     pseudo       VARCHAR(30) UNIQUE,
--     mdp          VARCHAR(256),
--     age          INTEGER,
--     mail         VARCHAR(50),
--     fan_pokemon  BOOLEAN
-- );

-- Table attendue
-- schema.public.utilisateur (ou ton schema .env)
-- id SERIAL PK, pseudo UNIQUE, password_hash TEXT NOT NULL
CREATE TABLE IF NOT EXISTS users (
  id             SERIAL PRIMARY KEY,
  pseudo         TEXT UNIQUE NOT NULL,
  password_hash  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages  (
  id             SERIAL PRIMARY KEY,
  conversation_id        TEXT UNIQUE NOT NULL,
  user_id  INT NULL,
  sender_type ENUM('user', 'ai') NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS conversations (
  id             SERIAL PRIMARY KEY,
  title         TEXT NOT NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations_participants (
  id             SERIAL PRIMARY KEY,
  conversation_id   INT NULL  ,
  user_id  INT NULL,
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(conversation_id, user_id) 
);

