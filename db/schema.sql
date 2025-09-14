-- HussEyquation Database Schema
-- Postgres SQL

create table players (
  player_id bigserial primary key,
  nba_player_id text unique,         -- from NBA.com via nba_api
  full_name text not null,
  primary_pos text
);

create table teams (
  team_id bigserial primary key,
  abbr text unique not null,
  name text
);

create table seasons (
  season_id int primary key,         -- 2016..2026 (year season ends)
  start_date date,
  end_date date,
  status text default 'historical'   -- 'historical'|'active'
);

create table snapshots (
  snapshot_id bigserial primary key,
  season_id int references seasons(season_id),
  snapshot_date date not null,
  source_hash text,
  created_at timestamptz default now()
);

create table player_snapshot_stats (
  snapshot_id bigint references snapshots(snapshot_id),
  player_id bigint references players(player_id),
  team_id bigint references teams(team_id),
  g int, mp int,
  per numeric(6,2),
  ws numeric(6,2),
  ws48 numeric(7,4),
  bmp numeric(6,2),
  vorp numeric(6,2),
  primary key (snapshot_id, player_id)
);

create table player_snapshot_ranks (
  snapshot_id bigint references snapshots(snapshot_id),
  player_id bigint references players(player_id),
  per_rank int, ws_rank int, ws48_rank int, bmp_rank int, vorp_rank int,
  huss_score numeric(7,3),
  huss_rank int,
  qualified boolean default true,
  primary key (snapshot_id, player_id)
);

create table season_final_ranks (
  season_id int references seasons(season_id),
  player_id bigint references players(player_id),
  per_rank int, ws_rank int, ws48_rank int, bmp_rank int, vorp_rank int,
  huss_score numeric(7,3),
  huss_rank int,
  qualified boolean default true,
  primary key (season_id, player_id)
);

create index ix_ranks_snapshot on player_snapshot_ranks (snapshot_id, huss_rank);
create index ix_ranks_qual on player_snapshot_ranks (snapshot_id, qualified, huss_rank);
create index ix_stats_team on player_snapshot_stats (snapshot_id, team_id);
create index ix_players_nbaid on players (nba_player_id);