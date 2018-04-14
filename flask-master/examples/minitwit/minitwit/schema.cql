drop keyspace if exists mt_api;
create keyspace mt_api
  with replication = {
    'class' : 'SimpleStrategy',
    'replication_factor' : 3
  };

use mt_api;

drop table if exists mt_api.user;
create table user (
  user_id uuid,
  username text,
  email text,
  pw_hash text,
  primary key (username, user_id)
);

drop table if exists mt_api.message;
create table message (
  user_id uuid,
  username text,
  date timestamp,
  message text,
  whom_id set<uuid>,
  who_id set<uuid>,
  primary key ((username, user_id), date, message)
) with clustering order by (date desc);

drop index if exists mt_api.user_user_id;
create index user_user_id on user(user_id);

drop index if exists mt_api.message_user_id;
create index message_user_id on message(user_id);

-- drop index if exists mt_api.message_username;
-- create index message_username on message(username);
