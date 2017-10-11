drop table if exists char_sheets;
create table char_sheets (
    id integer primary key autoincrement,
    author text not null,
    char_name text not null,
    char_class text not null,
    char_lvl integer not null,
    alignment text not null,
    curr_health integer not null,
    max_health integer not null,
    char_armor integer not null,
    char_str integer not null,
    char_dex integer not null,
    char_const integer not null,
    char_intel integer not null,
    char_wisdom integer not null,
    char_charisma integer not null,
    char_perception integer not null,
    char_weapons blob,
    char_inv blob,
    char_skills blob,
    char_notes blob
);

drop table if exists user_list;
create table user_list (
    id integer primary key autoincrement,
    username text not null,
    password
);
