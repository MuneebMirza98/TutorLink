INSERT INTO "role" ("id", "name") VALUES
(-1, 'Autre'),
(0, 'Professeur'),
(1, 'Doctorant'),
(2, 'Vacataire');

INSERT INTO "session_type" ("id", "name") VALUES
('CM', 'Cours Magistraux'),
('TAPE (ex CM-DIST)', 'Travail en autonomie planifié et encadré'),
('TD', 'Travaux Dirigés'),
('TP', 'Travaux Pratiques, Ateliers, Visites'),
('ORA', 'Jury de concours, soutenance, épreuve orale, entretien (ES) '),
('EXA', 'Evaluation des connaissances et capacités : DS, QCM, présentation orale'),
('APT', 'Travail en Autonomie programmé à l''EDT'),
('CL', 'Cours de langue'),
('PROJ', 'Projet : heures encadrées présentielles'),
('L', 'Séance d''information'),
('PRO-DIST', 'Projet à distance'),
('VISIT', 'Visites'),
('APTL', 'Travail Autonomie Libre, non programmé   l''EDT');

INSERT INTO "user" ("username", "email", "name", "surname", "role_id", "admin") VALUES
('amontarn', 'aurelie.montarnal@mines-albi.fr', 'Aurélie', 'Montarnal', 0, true),
('benaben', 'frederick.benaben@mines-albi.fr', 'Frédéric', 'Benaben', 0, false),
('cleduff', 'clara.le_duff@mines-albi.fr', 'Clara', 'Le Duff', 1, false),
('jlagarde', 'julien.lagarde@mines-albi.fr', 'Julien', 'Lagarde', -1, true),
('mmirza', 'muneeb.mirza@mines-albi.fr', 'Muneeb', 'Mirza', 1, true),
('gslaoui', 'ghali.slaoui@mines-albi.fr', 'Ghali', 'Slaoui', 1, true),
('afertier', 'audrey.fertier@mines-albi.fr', 'Audrey', 'Fertier', 0, false);

INSERT INTO "module" ("name", "label") VALUES
('MOD-IFIE3-G-S-ProjAgil-C1', 'Management agile de projets'),
('MOD-IFIE3-G-GSI-ASCII-C1', 'Application Specifications (ASCII)');

INSERT INTO "ue" ("name", "label") VALUES
('UE-IFIE3-GIPSI-S-OMng', 'Socle GIPSI : outils pour le management des organisations'),
('UE-IFIE3-GIPSI-GSI-ASD', 'GSI : Application Spécification et développement (ASIDE)');

INSERT INTO "session" ("id", "date_start", "date_end", "type", "module_id", "ue_id", "salle", "group_name") VALUES
(1, '2022-09-27 09:45', '2022-09-27 11:15', 'TD', 1, 1, '0F05-zoom, 51-140 pers - 0F05', 'IFIE3-GIPSI-GI2, IFIE3-GIPSI-GSI2'),
(2, '2022-09-27 11:30', '2022-09-27 13:00', 'TD', 1, 1, '0F05-zoom, 51-140 pers - 0F05', 'IFIE3-GIPSI-GI2, IFIE3-GIPSI-GSI2'),
(3, '2022-09-14 08:00', '2022-09-14 09:30', 'CM', 2, 2, '1A23-zoom, 30-50 pers - 1A23', 'IFIE3-GIPSI-GSI');

INSERT INTO "favorite" ("user_username", "module_id") VALUES
('cleduff', 1),
('benaben', 2);

INSERT INTO "lectured_by" ("session_id", "user_username") VALUES
(1, 'cleduff'),
(2, 'cleduff'),
(1, 'afertier'),
(2, 'afertier'),
(3, 'benaben');

INSERT INTO "managed_by" ("module_id", "user_username") VALUES
(1, 'cleduff'),
(2, 'benaben');