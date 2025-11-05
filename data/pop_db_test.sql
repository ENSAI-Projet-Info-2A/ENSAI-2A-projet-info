-- data/pop_db_test.sql
-- Peuplement cohérent avec hash_password (sha256 du mot_de_passe + pseudo)
-- Nécessite pgcrypto pour la fonction digest()

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Table: utilisateurs (pseudo TEXT, mot_de_passe TEXT, etc.)
-- Chaque mot de passe est haché comme dans le code Python :
-- hash_password(mdp, pseudo) = sha256(mdp || pseudo) → encode(..., 'hex')

INSERT INTO utilisateurs (pseudo, mot_de_passe) VALUES
('user_alpha',  encode(digest('P@ssw0rd1!' || 'user_alpha', 'sha256'), 'hex')),
('user_bravo',  encode(digest('S3cur3#'     || 'user_bravo', 'sha256'), 'hex')),
('charlie12',   encode(digest('qwertyT6!'   || 'charlie12',  'sha256'), 'hex')),
('delta_7',     encode(digest('D3ltaPwd'    || 'delta_7',    'sha256'), 'hex')),
('echo_99',     encode(digest('Echo!2025'   || 'echo_99',    'sha256'), 'hex')),
('foxtrot',     encode(digest('F0xtrot#9'   || 'foxtrot',    'sha256'), 'hex')),
('golf123',     encode(digest('G0lfBall7'   || 'golf123',    'sha256'), 'hex')),
('hotel_x',     encode(digest('H0t3lKey!'   || 'hotel_x',    'sha256'), 'hex')),
('india7',      encode(digest('Ind1aPass'   || 'india7',     'sha256'), 'hex')),
('juliet42',    encode(digest('JuLieT_42'   || 'juliet42',   'sha256'), 'hex'));

