INSERT INTO user VALUES
('fd9935df-0fe5-4b76-9202-d345ee7da5a3', 'thomas','tngo0508@gmail.com', 'pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d'),
('82527372-c403-47ba-88ea-61fddd34c180', 'bob', 'bob@example.com', 'pbkdf2:sha256:50000$ZccswADr$641523567028e8e6ffe6eb41be32c0f5687989a672f56f58754b149cb5de12b4');

INSERT INTO message VALUES
(1, 'fd9935df-0fe5-4b76-9202-d345ee7da5a3', 'hello, world!', 1518323568),
(2, 'fd9935df-0fe5-4b76-9202-d345ee7da5a3', 'second test', 1518323583),
(3, '82527372-c403-47ba-88ea-61fddd34c180', '123', 1518409690),
(4, '82527372-c403-47ba-88ea-61fddd34c180', 'second comment', 1518409714);

INSERT INTO follower VALUES
('fd9935df-0fe5-4b76-9202-d345ee7da5a3', '9502b0ad-0cf3-4ec7-b4c2-07593ffa0b5c'),
('fd9935df-0fe5-4b76-9202-d345ee7da5a3', '8eb934fd-47a2-4953-b203-18bfd00cd9ef'),
('fd9935df-0fe5-4b76-9202-d345ee7da5a3', '9502b0ad-0cf3-4ec7-b4c2-07593ffa0b5c'),
('fd9935df-0fe5-4b76-9202-d345ee7da5a3', 'f7060ed1-008a-4dde-bae5-01fb05f2c27a');
