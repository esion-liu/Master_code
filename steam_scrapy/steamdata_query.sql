
# Remove duplication from table and add constraint: game_reviews
create table temp_table as
select distinct on (game_name, reviewer_name) *
from game_reviews gr 
order by game_name, reviewer_name, id;

alter table game_reviews rename to temp_table1;

alter table temp_table rename to game_reviews;

drop table temp_table1;

alter table games
add constraint unique_name_column unique (name);

# Remove duplication from table and add constraint: games
delete from games
where id not in (
	select min(id)
	from games
	group by name
);

alter table game_reviews
add constraint unique_game_reviewer unique (game_name, reviewer_name);

# Some common queries

# List all records
SELECT * FROM games;
SELECT * FROM game_reviews;

# Number of records in both tables
select count(*) from games;
select count(*) from game_reviews gr ;

# Check the number of players who have made equal or more than 50 reviews.
select count(*)
from(select reviewer_name, count(game_name) as cg
from steam.public.game_reviews gr 
group by reviewer_name
order by cg desc) as rc
where rc.cg > 49/29;

# Make a backup to review table
create table game_reviews_bp as
select * from game_reviews gr 