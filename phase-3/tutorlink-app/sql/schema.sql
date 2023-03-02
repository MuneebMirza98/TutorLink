-- Initialize the database.
-- Drop any existing data and create empty tables.
-- 
-- psql "postgresql://tutorlinkadmin:tutorlinkadminpass@localhost:5432/tutorlink" < sql/schema.sql
-- 

drop table if exists "user" cascade;
drop table if exists session cascade;
drop table if exists module cascade;
drop table if exists ue cascade;
drop table if exists favorite cascade;
drop table if exists managed_by cascade;
drop table if exists role cascade;
drop table if exists lectured_by cascade;
drop table if exists session_type cascade;


create table role (
    id integer primary key,
    name text not null
);


create table session_type (
    id text primary key,
    name text not null
);


create table "user" (
  username text primary key,
  email text,
  name text,
  surname text,
  role_id integer,
  admin boolean default false,
  foreign key (role_id) references role(id)
);


create table module (
    id serial primary key,
    name text not null,
    label text not null,
    description text
);


create table ue (
    id serial primary key,
    name text not null,
    label text not null
);


create table session (
    id integer primary key,
    date_start timestamp not null,
    date_end timestamp not null,
    type text not null,
    module_id integer not null,
    ue_id integer not null,
    salle text,
    group_name text,
    foreign key (module_id) references module(id),
    foreign key (ue_id) references ue(id),
    foreign key (type) references session_type(id)
);


create table favorite (
    user_username text not null,
    module_id integer not null,
    primary key (user_username, module_id),
    foreign key (module_id) references module(id),
    foreign key (user_username) references "user"(username)
);


create table lectured_by (
    session_id integer not null,
    user_username text not null,
    synapse boolean default false,
    primary key (session_id, user_username),
    foreign key (session_id) references session(id),
    foreign key (user_username) references "user"(username)
);


create table managed_by (
    module_id integer not null,
    user_username text not null,
    primary key (module_id, user_username),
    foreign key (module_id) references module(id),
    foreign key (user_username) references "user"(username)
);
