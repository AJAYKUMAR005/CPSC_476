insert into mt_api.user (user_id, username, email, pw_hash) values
  (ba4f7e02-a5d1-4c60-9a95-de51142aa51a, 'thomas', 'tngo0508@gmail.com', 'pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d');
insert into mt_api.user (user_id, username, email, pw_hash) values
  (c405ae0d-b7f1-44dd-8c95-f442fea668ab, 'bob', 'bob@gmail.com', 'pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d');
insert into mt_api.user (user_id, username, email, pw_hash) values
  (cfca912b-eaaa-449f-8162-682289e23e4b, 'eve', 'eve@gmail.com', 'pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d');
insert into mt_api.user (user_id, username, email, pw_hash) values
  (d68a329e-caac-4114-8e0b-e3be895fb538, 'smith', 'smith@gmail.com', 'pbkdf2:sha256:50000$r1fUXyrZ$5908841c968862270f5a49550fa46d188680922d2c9c3e571f75fa248034d09d');

insert into mt_api.message (user_id, username, date, message, whom_id, who_id) VALUES
  (ba4f7e02-a5d1-4c60-9a95-de51142aa51a, 'thomas', '2018-04-14 07:22:28', 'hello world', {c405ae0d-b7f1-44dd-8c95-f442fea668ab, cfca912b-eaaa-449f-8162-682289e23e4b}, {cfca912b-eaaa-449f-8162-682289e23e4b, d68a329e-caac-4114-8e0b-e3be895fb538});
insert into mt_api.message (user_id, username, date, message, whom_id, who_id) VALUES
  (ba4f7e02-a5d1-4c60-9a95-de51142aa51a, 'thomas', '2018-04-17 06:22:35', 'testing population', {c405ae0d-b7f1-44dd-8c95-f442fea668ab, cfca912b-eaaa-449f-8162-682289e23e4b}, {cfca912b-eaaa-449f-8162-682289e23e4b, d68a329e-caac-4114-8e0b-e3be895fb538});
insert into mt_api.message (user_id, username, date, message, whom_id, who_id) VALUES
  (c405ae0d-b7f1-44dd-8c95-f442fea668ab, 'bob', '2017-03-14 02:21:38', 'hello from bob', {ba4f7e02-a5d1-4c60-9a95-de51142aa51a, cfca912b-eaaa-449f-8162-682289e23e4b}, {cfca912b-eaaa-449f-8162-682289e23e4b, d68a329e-caac-4114-8e0b-e3be895fb538});
insert into mt_api.message (user_id, username, date, message, whom_id, who_id) VALUES
  (c405ae0d-b7f1-44dd-8c95-f442fea668ab, 'bob', '2018-04-17 10:00:28', 'testing from bob', {ba4f7e02-a5d1-4c60-9a95-de51142aa51a, cfca912b-eaaa-449f-8162-682289e23e4b}, {cfca912b-eaaa-449f-8162-682289e23e4b, d68a329e-caac-4114-8e0b-e3be895fb538});
insert into mt_api.message (user_id, username, date, message, who_id) VALUES
  (cfca912b-eaaa-449f-8162-682289e23e4b, 'eve', '2018-04-15 02:29:32', 'backend practice eve', {d68a329e-caac-4114-8e0b-e3be895fb538});
insert into mt_api.message (user_id, username, date, message, whom_id) VALUES
  (d68a329e-caac-4114-8e0b-e3be895fb538, 'smith', '2018-04-15 05:29:00', 'hi from smith', {ba4f7e02-a5d1-4c60-9a95-de51142aa51a, c405ae0d-b7f1-44dd-8c95-f442fea668ab});
