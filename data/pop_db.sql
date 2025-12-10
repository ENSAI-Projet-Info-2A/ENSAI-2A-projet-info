-- CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;

-- INSERT INTO utilisateurs (pseudo, mot_de_passe)
-- VALUES ('admin', encode(digest('admin' || 'admin', 'sha256'), 'hex'));

INSERT INTO prompts (nom, contenu)
VALUES ('default', 'Tu es un assistant utile.'),
('Formel', 'Tu es un assistant utile. Adopte un ton formel, précis et professionnel dans toutes tes réponses.'),
('Humour', 'Tu es un assistant utile. Réponds avec un ton léger et un humour subtil, sans nuire à la clarté.'), 
('Résumé', 'Tu es un assistant utile. Fournis des réponses concises et propose systématiquement un résumé clair en fin de message.'),
('Philippe Etchebest', 'Tu es Philippe Etchebest, chef cuisinier français reconnu pour ton exigence, 
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

BEGIN;

-----------------------------------------------------
-- 1. Utilisateurs (Géraldine & co)
-----------------------------------------------------

INSERT INTO utilisateurs (id, pseudo, mot_de_passe, temps_utilisation)
VALUES
  -- Mot de passe en clair : "Mamie!2025"
  (1, 'geraldine', 'b740ae7c854841f4e2b030d04ce42dc07558a3f03c7b2e66710a46d28693494c', NULL),

  -- Mot de passe en clair : "Belote&2025"
  (2, 'gilbert',   '8d9ab1d2175a0807069a00c9fb364f2ac7487c752d4d9b19600e722f6e611af1', NULL),

  -- Mot de passe en clair : "FilleGeraldine2025"
  (3, 'chantal',   '2ec08dfe48dc0f6efced9ade809d43e4905ba5a7551c02e3e2d8c1a33e0ec382', NULL)

ON CONFLICT (id) DO NOTHING;

-----------------------------------------------------
-- 2. Prompts
-----------------------------------------------------

INSERT INTO prompts (id, nom, contenu, version)
VALUES
  (1, 'fr_tutor_general',
$$Tu es un assistant bienveillant qui aide des utilisatrices peu habituées au numérique,
comme une grand-mère, à utiliser l''application et à discuter simplement.$$,
   1),

  (2, 'fr_mamie_cuisine',
$$Tu es un chef bienveillant spécialisé dans les recettes traditionnelles françaises.
Tu expliques les choses simplement à une grand-mère nommée Géraldine.$$,
   1)
ON CONFLICT (id) DO NOTHING;

-----------------------------------------------------
-- 3. Conversations
--   On force des IDs pour s'y retrouver :
--   101 : prise en main
--   102 : apprendre le bridge (Géraldine + Gilbert)
--   103 : crêpes Raymond Oliver (recette à retrouver)
--   104 : idées de menus de Noël
--   105 : organiser l'anniversaire de Léo
--   106 : petites astuces de jardinage
-----------------------------------------------------

INSERT INTO conversations (id, titre, proprietaire_id, prompt_id, cree_le)
VALUES
  (101, 'Prendre en main l''application', 1, 1, now() - interval '20 days'),
  (102, 'Apprendre à jouer au bridge',    1, 1, now() - interval '15 days'),
  (103, 'Recette de la pâte à crêpes du chef Raymond Oliver', 1, 2, now() - interval '10 days'),
  (104, 'Idées de menus de Noël en famille', 1, 2, now() - interval '5 days'),
  (105, 'Organiser l''anniversaire de Léo', 1, 1, now() - interval '3 days'),
  (106, 'Petites astuces de jardinage pour le balcon', 1, 1, now() - interval '2 days')
ON CONFLICT (id) DO NOTHING;

-----------------------------------------------------
-- 4. Participants aux conversations
--   Important pour respecter la contrainte sur messages
-----------------------------------------------------

-- Géraldine est dans toutes ses conversations
INSERT INTO conversations_participants (conversation_id, utilisateur_id)
VALUES
  (101, 1),
  (102, 1),
  (103, 1),
  (104, 1),
  (105, 1),
  (106, 1)
ON CONFLICT DO NOTHING;

-- -- Gilbert est invité sur la conversation "Apprendre à jouer au bridge"
-- INSERT INTO conversations_participants (conversation_id, utilisateur_id)
-- VALUES
--   (102, 2)
-- ON CONFLICT DO NOTHING;

-- Chantal apparaît dans la conversation "Organiser l'anniversaire de Léo"
INSERT INTO conversations_participants (conversation_id, utilisateur_id)
VALUES
  (105, 3)
ON CONFLICT DO NOTHING;

-----------------------------------------------------
-- 5. Messages
--   NB : on laisse l'id en SERIAL, pas besoin de le spécifier.
--   emetteur = 'utilisateur' => utilisateur_id NON NULL
--   emetteur = 'ia'          => utilisateur_id NULL
-----------------------------------------------------

-------------------------------
-- 5.1 Conversation 101 : Prise en main
-------------------------------
INSERT INTO messages (conversation_id, utilisateur_id, emetteur, contenu, cree_le)
VALUES
  (101, 1, 'utilisateur',
   $$Bonjour mon petit assistant, je suis Géraldine.
Je ne suis pas très douée avec les écrans, tu peux m’expliquer doucement comment te parler ?$$,
   now() - interval '20 days'),

  (101, NULL, 'ia',
   $$Bonjour Géraldine, avec plaisir 😊
Tu peux simplement écrire comme tu viens de le faire.
Par exemple :
- me demander une recette,
- me poser une question sur un sujet,
- ou juste papoter un peu.

Je te répondrai toujours le plus clairement possible.$$,
   now() - interval '20 days' + interval '2 minutes'),

  (101, 1, 'utilisateur',
   $$D’accord, je vais essayer de ne pas tout casser alors.
Merci, tu es bien plus patient que mon Gilbert quand il m’explique l’ordinateur !$$,
   now() - interval '20 days' + interval '5 minutes');

-------------------------------
-- 5.2 Conversation 102 : Apprendre à jouer au bridge (avec Gilbert)
-------------------------------
INSERT INTO messages (conversation_id, utilisateur_id, emetteur, contenu, cree_le)
VALUES
  (102, 1, 'utilisateur',
   $$Coucou, c’est encore Géraldine.
Je voudrais apprendre à jouer au bridge, car à la maison de quartier elles sont toutes accro et je ne comprends rien.
Tu peux m’expliquer les bases simplement ?$$,
   now() - interval '15 days'),

  (102, NULL, 'ia',
   $$Bien sûr Géraldine !
Le bridge est un jeu de cartes qui se joue à 4 joueurs, en deux équipes de 2.
Les grandes étapes :
1) La donne : on distribue les cartes.
2) L’enchère : chaque joueur annonce combien de levées son équipe pense faire.
3) Le jeu de la carte : on joue les plis en suivant la couleur demandée si possible.
4) Le score : on compte les levées réussies.

On peut y aller étape par étape, tranquillement.$$,
   now() - interval '15 days' + interval '2 minutes'),

  (102, 1, 'utilisateur',
   $$Très bien, on ira doucement hein.
Je vais inviter mon ami Gilbert sur cette conversation, il adore les cartes.
Par contre il triche à la belote, alors attention !$$,
   now() - interval '15 days' + interval '5 minutes'),

   (102, NULL, 'ia',
    $$Super faisons ça avec Gilbert !
 Je te laisse ajouter Gilbert.
 Alors on va partir de ce que tu connais à la belote pour t’expliquer le bridge.
 Par exemple, on retrouve la notion de levées, mais l’organisation et les enchères sont très différentes.
 Si vous voulez, je peux vous proposer un petit exercice de départ.$$,
    now() - interval '15 days' + interval '10 minutes');

-------------------------------
-- 5.3 Conversation 103 : Recette de la pâte à crêpes du chef Raymond Oliver
--     => C'est celle que Géraldine devra retrouver pendant la démo
-------------------------------
INSERT INTO messages (conversation_id, utilisateur_id, emetteur, contenu, cree_le)
VALUES
  -- Question de Géraldine
  (103, 1, 'utilisateur',
   $$Bonjour, c’est Géraldine.
J’ai entendu parler d’une recette de pâte à crêpes du chef Raymond Oliver.
Tu pourrais me donner la recette complète, avec les ingrédients et la préparation ?$$,
   now() - interval '10 days'),

  -- UNE SEULE réponse de l'IA, complète
  (103, NULL, 'ia',
   $$Bien sûr Géraldine, voici la recette complète de la pâte à crêpes du chef Raymond Oliver.

Ingrédients :
- 2 grosses pincées de sel
- 1 gousse de vanille
- 25 cl de lait
- 4 cuillères à soupe de sucre
- 400 g de farine
- 2 cuillères à soupe d'huile
- 8 œufs
- 100 g de beurre fondu
- 12,5 cl de pastis
- 25 cl de rhum
- 50 cl de bière

Préparation :
1. Faites chauffer dans une casserole le lait avec le sel, le sucre et la vanille fendue.
2. Lorsqu'il est bien chaud, ajoutez le beurre pour le faire fondre.
3. Versez la farine dans un saladier, formez un puits et versez-y l'huile et les œufs. Mélangez bien.
4. Ajoutez le lait chaud en plusieurs fois en mélangeant pour éviter les grumeaux.
5. Ajoutez ensuite le pastis et le rhum.
6. Allongez la pâte avec la bière jusqu'à obtenir une pâte bien claire et fluide.
7. Faites cuire la pâte dans une poêle bien chaude, sans ajouter de matière grasse (le beurre de la pâte suffit).

Conseils :
- Les ingrédients doivent être à température ambiante pour que la pâte ne soit ni trop froide ni trop chaude.
- La quantité d’œufs peut être variable : n'hésite pas à en ajouter pour ajuster la texture.
- La pâte doit rester très claire et liquide pour donner des crêpes fines et légères.

Avec cette pâte à crêpes de Raymond Oliver, tu vas faire des heureux à la maison, Géraldine 🥞$$,
   now() - interval '10 days' + interval '3 minutes'),

  -- Réponse de Géraldine
  (103, 1, 'utilisateur',
   $$Oh là là, ça a l’air délicieux !
Je vais noter ça dans mon cahier à recettes et en faire pour les petits-enfants ce week-end.
Merci mon petit assistant.$$,
   now() - interval '10 days' + interval '8 minutes');

-------------------------------
-- 5.4 Conversation 104 : Idées de menus de Noël
-------------------------------
INSERT INTO messages (conversation_id, utilisateur_id, emetteur, contenu, cree_le)
VALUES
  (104, 1, 'utilisateur',
   $$Rebonjour, c’est encore Géraldine.
Cette fois je cherche des idées de menus de Noël en famille, mais pas trop compliqués à préparer pour une mamie fatiguée.$$,
   now() - interval '5 days'),

  (104, NULL, 'ia',
   $$Très bien Géraldine, on va faire simple et gourmand.

Idée de menu de Noël :
- Entrée : velouté de potimarron et châtaignes
- Plat : rôti de dinde ou de pintade aux marrons, avec une purée de pommes de terre
- Dessert : bûche de Noël légère aux fruits ou une salade d’agrumes.

On peut détailler les recettes si tu veux, ou adapter selon ce que ta famille aime.$$,
   now() - interval '5 days' + interval '3 minutes'),

  (104, 1, 'utilisateur',
   $$Parfait, il me faut aussi une recette de bûche très simple, je n’ai plus l’énergie de faire des choses compliquées.
On pourra voir ça plus tard.$$,
   now() - interval '5 days' + interval '8 minutes');

-------------------------------
-- 5.5 Conversation 105 : Anniversaire de Léo (avec Chantal)
-------------------------------
INSERT INTO messages (conversation_id, utilisateur_id, emetteur, contenu, cree_le)
VALUES
  (105, 1, 'utilisateur',
   $$Bonjour, c’est encore Géraldine.
Je veux organiser l’anniversaire de mon petit-fils Léo qui va avoir 8 ans.
Tu as des idées de jeux calmes (pas trop de bazar dans mon salon) ?$$,
   now() - interval '3 days'),

  (105, NULL, 'ia',
   $$Super projet Géraldine !

Idées de jeux calmes pour 8 ans :
- Jeux de société (Uno, Dobble, petits jeux de plateau)
- Atelier dessin ou coloriage sur une grande table
- Petit concours de devinettes
- Atelier décoration de cupcakes ou de sablés.

On peut aussi prévoir un temps pour souffler les bougies et ouvrir les cadeaux tranquillement.$$,
   now() - interval '3 days' + interval '3 minutes'),

  (105, 3, 'utilisateur',
   $$Maman, c’est Chantal.
Léo adore les énigmes, tu peux lui préparer un petit jeu de piste dans l’appartement, avec des indices simples ?$$,
   now() - interval '3 days' + interval '7 minutes'),

  (105, NULL, 'ia',
   $$Bonjour Chantal !
Très bonne idée : on peut créer un mini jeu de piste avec 5 à 6 étapes,
des énigmes très simples (devinettes, observation d’objets dans le salon),
et un petit trésor à la fin : les bonbons ou le gâteau de mamie Géraldine 😉$$,
   now() - interval '3 days' + interval '10 minutes');

-------------------------------
-- 5.6 Conversation 106 : Jardinage
-------------------------------
INSERT INTO messages (conversation_id, utilisateur_id, emetteur, contenu, cree_le)
VALUES
  (106, 1, 'utilisateur',
   $$Dis-moi, j’ai un petit balcon plein nord.
Est-ce que tu peux me conseiller des plantes faciles pour une mamie qui oublie parfois d’arroser ?$$,
   now() - interval '2 days'),

  (106, NULL, 'ia',
   $$Bien sûr Géraldine !

Pour un balcon à l’ombre et peu d’arrosage, tu peux essayer :
- Les fougères (certaines variétés supportent bien l’ombre),
- Le lierre,
- Les hostas (très décoratifs),
- Certaines variétés de bégonias.

On peut faire un plan de balcon ensemble si tu veux, étape par étape.$$,
   now() - interval '2 days' + interval '3 minutes');

-----------------------------------------------------
-- 6. Ajustement des séquences (optionnel mais propre)
--   => utile si tu as forcé des id
-----------------------------------------------------

SELECT setval(pg_get_serial_sequence('utilisateurs', 'id'),
              (SELECT MAX(id) FROM utilisateurs), true);

SELECT setval(pg_get_serial_sequence('prompts', 'id'),
              (SELECT MAX(id) FROM prompts), true);

SELECT setval(pg_get_serial_sequence('conversations', 'id'),
              (SELECT MAX(id) FROM conversations), true);

COMMIT;
