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



INSERT INTO conversations (id, titre, prompt_id, cree_le) VALUES
(1, 'Recette de pastèque au maroilles', 1, '2025-01-12 10:23:45+00'),
(2, 'comment faire disparaître un corps rapidement', 1, '2025-02-03 22:41:09+00'),
(3, 'comment diagonaliser une matrice', 1, '2025-03-15 09:12:30+00'),
(4, 'j''ai peur des fraises et j''ai 50 ans', 1, '2025-04-28 17:05:12+00'),
(5, 'j''ai regardé one piece et depuis je vote à gauche', 1, '2025-05-09 14:56:33+00'),
(6, 'j''adore Harry potter et Bernard Henry-Levy', 1, '2025-07-21 08:44:18+00'),
(7, 'pourquoi la terre est plate ?', 1, '2025-09-11 23:19:00+00'),
(8, 'Je suis fan de tokyo hotel et ma femme m''a quitté', 1, '2025-10-30 12:31:55+00');



INSERT INTO conversations_participants (id, conversation_id, utilisateur_id) VALUES
(1, 2, 10),
(1, 2, 4),
(1, 2, 6),
(2, 1, 9),
(3, 4, 8),
(4, 3, 7),
(4, 3, 2),
(4, 3, 9)
(5, 6, 6),
(6, 5, 5),
(7, 8, 4),
(8, 7, 3);


