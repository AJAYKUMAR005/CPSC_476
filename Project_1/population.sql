INSERT INTO user VALUES
(1, 'thomas','tngo0508@gmail.com', 'pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d'),
(2, 'bob', 'bob@example.com', 'pbkdf2:sha256:50000$ZccswADr$641523567028e8e6ffe6eb41be32c0f5687989a672f56f58754b149cb5de12b4'),
(3, 'eve', 'eve@csu.fullerton.edu', 'pbkdf2:sha256:50000$XArlgzMX$73e58aef7c4ffd196acab89ae912837172583170d794bc29370193731a437bf0');

INSERT INTO message VALUES
(1, 1, 'hello, world!', 1518323568),
(2, 1, 'second test', 1518323583),
(3, 2, '123', 1518409690),
(4, 2, 'second comment', 1518409714),
(5, 2, 'third post', 1518409719),
(6, 3, 'hi', 1518409764),
(7, 3, '12345678', 1518409781),
(8, 3, 'foo', 1518409786),
(9, 3, 'bar', 1518409808),
(10, 1, 'test following', 1518409832),
(11, 1, 'I am practicing web service API', 1518409844),
(12, 1, 'populates database for testing', 1518409848);

INSERT INTO follower VALUES
(2, 1),
(3, 2),
(3, 1);
