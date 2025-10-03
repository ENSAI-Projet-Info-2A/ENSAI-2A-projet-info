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
CREATE TABLE IF NOT EXISTS utilisateur (
  id             SERIAL PRIMARY KEY,
  pseudo         TEXT UNIQUE NOT NULL,
  password_hash  TEXT NOT NULL
);