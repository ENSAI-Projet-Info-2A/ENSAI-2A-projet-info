-- INSERT INTO joueur(id_joueur, pseudo, mdp, age, mail, fan_pokemon) VALUES
-- (999, 'admin',      '0000',     0,       'admin@projet.fr',      null),
-- (998, 'a',             'a',     20,      'a@ensai.fr',           true),
-- (997, 'maurice',    '1234',     20,      'maurice@ensai.fr',     true),
-- (996, 'batricia',   '9876',     25,      'bat@projet.fr',        false),
-- (995, 'miguel',     'abcd',     23,      'miguel@projet.fr',     true),
-- (994, 'gilbert',    'toto',     21,      'gilbert@projet.fr',    false),
-- (993, 'junior',     'aaaa',     15,      'junior@projet.fr',     true);

-- data/pop_db_test.sql (10 utilisateurs de test)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO utilisateurs (pseudo, mot_de_passe) VALUES
('user_alpha',   crypt('P@ssw0rd1!',    gen_salt('bf', 12))),
('user_bravo',   crypt('S3cur3#',       gen_salt('bf', 12))),
('charlie12',    crypt('qwertyT6!',     gen_salt('bf', 12))),
('delta_7',      crypt('D3ltaPwd',      gen_salt('bf', 12))),
('echo_99',      crypt('Echo!2025',     gen_salt('bf', 12))),
('foxtrot',      crypt('F0xtrot#9',     gen_salt('bf', 12))),
('golf123',      crypt('G0lfBall7',     gen_salt('bf', 12))),
('hotel_x',      crypt('H0t3lKey!',     gen_salt('bf', 12))),
('india7',       crypt('Ind1aPass',     gen_salt('bf', 12))),
('juliet42',     crypt('JuLieT_42',     gen_salt('bf', 12)));

