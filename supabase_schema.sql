-- Frisco Bowl Bot — Supabase schema
-- Run this in the Supabase SQL Editor for your new project
-- (Project → SQL Editor → New query → paste → Run)

create table if not exists notable_players (
    id bigint generated always as identity primary key,
    player_name text not null unique,      -- must match nflverse's player_display_name exactly
    school text,                            -- optional: college/team they played for
    frisco_bowl_year int,                   -- optional: year they played in the Frisco Bowl
    notes text,                             -- optional: anything else worth remembering
    created_at timestamptz not null default now()
);

-- Simple, no auth required — anyone with the anon key can read/write.
-- Fine for a low-stakes internal tool; tighten later with RLS + auth if needed.
alter table notable_players enable row level security;

create policy "Allow all access to notable_players"
    on notable_players
    for all
    using (true)
    with check (true);

-- Example inserts (edit/remove as needed):
-- insert into notable_players (player_name, school, frisco_bowl_year) values
--   ('Patrick Mahomes', 'Texas Tech', 2013),
--   ('Player Name', 'School', 2022);
