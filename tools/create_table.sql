create table stations (
    pref varchar(10),
    line varchar(30),
    station varchar(30),
    lon double precision,
    lat double precision,
    primary key (pref, line, station)
);