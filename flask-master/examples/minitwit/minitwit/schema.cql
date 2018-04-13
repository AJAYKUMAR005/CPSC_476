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
  primary key ((username, user_id), date)
);
