drop table if exists char_sheets;
create table char_sheets (
    id integer primary key autoincrement,
    char_name text not null,
    char_class text not null,
    char_lvl integer not null
);
