INSERT INTO user VALUES
('9502b0ad-0cf3-4ec7-b4c2-07593ffa0b5c', 'john', 'john@csu.fullerton.edu', 'pbkdf2:sha256:50000$XArlgzMX$73e58aef7c4ffd196acab89ae912837172583170d794bc29370193731a437bf0'),
('f7060ed1-008a-4dde-bae5-01fb05f2c27a', 'steve', 'steve@csu.fullerton.edu', 'pbkdf2:sha256:50000$XArlgzMX$73e58aef7c4ffd196acab89ae912837172583170d794bc29370193731a437bf0');

INSERT INTO message VALUES
(1, '9502b0ad-0cf3-4ec7-b4c2-07593ffa0b5c', 'third post', 1518409719),
(2, '9502b0ad-0cf3-4ec7-b4c2-07593ffa0b5c', 'hi', 1518409764),
(3, 'f7060ed1-008a-4dde-bae5-01fb05f2c27a', '12345678', 1518409781),
(4, 'f7060ed1-008a-4dde-bae5-01fb05f2c27a', 'foo', 1518409786),
(5, 'f7060ed1-008a-4dde-bae5-01fb05f2c27a', 'bar', 1518409808),
(6, 'f7060ed1-008a-4dde-bae5-01fb05f2c27a', 'test following', 1518409832);

INSERT INTO follower VALUES
('9502b0ad-0cf3-4ec7-b4c2-07593ffa0b5c', 'f7060ed1-008a-4dde-bae5-01fb05f2c27a'),
('9502b0ad-0cf3-4ec7-b4c2-07593ffa0b5c', '8eb934fd-47a2-4953-b203-18bfd00cd9ef'),
('f7060ed1-008a-4dde-bae5-01fb05f2c27a', '9502b0ad-0cf3-4ec7-b4c2-07593ffa0b5c'),
('f7060ed1-008a-4dde-bae5-01fb05f2c27a', 'a6d0fcf6-e3c7-4868-94eb-dc27136bf649');
