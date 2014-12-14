CREATE TABLE account 
(
    ip varchar(20) primary key, 
    hash varchar(512) NOT NULL, 
    salt varchar(512) NOT NULL
);

CREATE TABLE bot_status 
(
    ip varchar(20) primary key, 
    last_startup_time timestamp, 
    last_shutdown_time timestamp, 
    last_activity_time timestamp, 
    port integer, 
    message varchar(100)
);

CREATE TABLE command_log 
(
    command_id integer primary key, 
    time timestamp NOT NULL, 
    content text NOT NULL
);

CREATE TABLE command_map 
(
    command_id integer references command_log(command_id) NOT NULL,
    bot_ip text NOT NULL,
    primary key(command_id, bot_ip)
);

