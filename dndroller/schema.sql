drop table if exists user_database;
create table user_database (
    id integer primary key autoincrement,
    username text not null,
    password text not null
);
