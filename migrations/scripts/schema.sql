create type user_types AS ENUM (
    'admin',
    'user',
    'external',
    'fake'
);

create table customers
(
    id                           serial not null
        constraint customers_pk
            primary key,
    first_name                   varchar,
    last_name                    varchar,
    email                        varchar,
    subdomain                    varchar,
    go1_active                   bool,
    go1_id                       integer,
    user_type                    user_types,
    created_at                   timestamp with time zone,
    updated_at                   timestamp with time zone
);

alter table customers
    owner to postgres;

create unique index customers_id_uindex
    on customers (id);

create unique index customers_email_uindex
    on customers (email);

create unique index customers_go1_id_uindex
    on customers (go1_id);
