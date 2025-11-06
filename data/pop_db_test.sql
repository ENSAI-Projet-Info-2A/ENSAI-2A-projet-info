-- data/pop_db_test.sql
-- Peuplement cohérent avec hash_password (sha256 du mot_de_passe + pseudo)
-- Nécessite pgcrypto pour la fonction digest()

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Table: utilisateurs (pseudo TEXT, mot_de_passe TEXT, etc.)
-- Chaque mot de passe est haché comme dans le code Python :
-- hash_password(mdp, pseudo) = sha256(mdp || pseudo) → encode(..., 'hex')

INSERT INTO utilisateurs (id, pseudo, mot_de_passe) VALUES
(1, 'user_alpha',  encode(digest('P@ssw0rd1!' || 'user_alpha', 'sha256'), 'hex')),
(2, 'user_bravo',  encode(digest('S3cur3#'     || 'user_bravo', 'sha256'), 'hex')),
(3, 'charlie12',   encode(digest('qwertyT6!'   || 'charlie12',  'sha256'), 'hex')),
(4, 'delta_7',     encode(digest('D3ltaPwd'    || 'delta_7',    'sha256'), 'hex')),
(5, 'echo_99',     encode(digest('Echo!2025'   || 'echo_99',    'sha256'), 'hex')),
(6, 'foxtrot',     encode(digest('F0xtrot#9'   || 'foxtrot',    'sha256'), 'hex')),
(7, 'golf123',     encode(digest('G0lfBall7'   || 'golf123',    'sha256'), 'hex')),
(8, 'hotel_x',     encode(digest('H0t3lKey!'   || 'hotel_x',    'sha256'), 'hex')),
(9, 'india7',      encode(digest('Ind1aPass'   || 'india7',     'sha256'), 'hex')),
(10, 'juliet42',    encode(digest('JuLieT_42'   || 'juliet42',   'sha256'), 'hex'));

-- prompts
INSERT INTO prompts(id, nom, contenu,version) VALUES
(1,'fr_tuteur_strict_v2','Tu es tuteur strict en français.Corrige toutes les fautes d''orthographe et de grammaire.',1)
(2,'math_tuteur','Tu es tuteur en maths.Expliquer les concepts fondamentaux de la geometrie',2)
(3,'codeur_python','vous êtes un excellent codeur python. Veuillez expliquer les concepts suivants:mock, swagg',1)
(4,'math_prof', 'Tu es un professeur de mathématiques patient. Explique les concepts étape par étape avec des exemples concrets.', 3),


