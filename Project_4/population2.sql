INSERT INTO user VALUES
('a6d0fcf6-e3c7-4868-94eb-dc27136bf649', 'eve', 'eve@csu.fullerton.edu', 'pbkdf2:sha256:50000$XArlgzMX$73e58aef7c4ffd196acab89ae912837172583170d794bc29370193731a437bf0'),
('8eb934fd-47a2-4953-b203-18bfd00cd9ef', 'marry', 'marry@csu.fullerton.edu', 'pbkdf2:sha256:50000$XArlgzMX$73e58aef7c4ffd196acab89ae912837172583170d794bc29370193731a437bf0');

INSERT INTO message VALUES
(1, 'a6d0fcf6-e3c7-4868-94eb-dc27136bf649', 'I am practicing web service API', 1518409844),
(2, 'a6d0fcf6-e3c7-4868-94eb-dc27136bf649', 'populates database for testing', 1518409848);

INSERT INTO follower VALUES
('a6d0fcf6-e3c7-4868-94eb-dc27136bf649', 'f7060ed1-008a-4dde-bae5-01fb05f2c27a'),
('a6d0fcf6-e3c7-4868-94eb-dc27136bf649', 'fd9935df-0fe5-4b76-9202-d345ee7da5a3'),
('8eb934fd-47a2-4953-b203-18bfd00cd9ef', '9502b0ad-0cf3-4ec7-b4c2-07593ffa0b5c'),
('8eb934fd-47a2-4953-b203-18bfd00cd9ef', 'fd9935df-0fe5-4b76-9202-d345ee7da5a3');
