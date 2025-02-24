select distinct genres, count(genres) as cnt
from game_info gi, game_review gr 
where gr.game = gi.title 
group by genres 
order by cnt desc;

--common game genres: 
--Action: Action
--Shotting: FPS, Shoot
--RPG and Adventure: RPG, Adventure
--Strategy: Strategy, Tactics
--Platformer: Platformer
--Survival: Survival
--Racing: Racing
--Fighting: Fighting
--Sports: Soccer, Football, Basketball, Tennis, Baseball, Sports, Biking

-- Action games critic
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Action%'
and gr.critic_or_not
ORDER BY RANDOM()

-- Action game user
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Action%'
and not gr.critic_or_not
ORDER BY RANDOM()

--shooting game critic
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and (gi.genres like '%FPS%' OR gi.genres like '%Shoot%')
and gr.critic_or_not
ORDER BY RANDOM()

--shooting game user
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and (gi.genres like '%FPS%' OR gi.genres like '%Shoot%')
and not gr.critic_or_not
ORDER BY RANDOM()

--RPG and ADV critic
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and (gi.genres like '%RPG%' OR gi.genres like '%Adventure%')
and gr.critic_or_not
ORDER BY RANDOM()

--RPG and ADV user
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and (gi.genres like '%RPG%' OR gi.genres like '%Adventure%')
and not gr.critic_or_not
ORDER BY RANDOM()

--Strategy critic
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and (gi.genres like '%Strategy%' OR gi.genres like '%Tactics%')
and gr.critic_or_not
ORDER BY RANDOM()

--Strategy user
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and (gi.genres like '%Strategy%' OR gi.genres like '%Tactics%')
and not gr.critic_or_not
ORDER BY RANDOM()

--Platformer critic
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Platformer%'
and gr.critic_or_not
ORDER BY RANDOM()

--Platformer user
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Platformer%'
and not gr.critic_or_not
ORDER BY RANDOM()

--Survival critic
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Survival%'
and gr.critic_or_not
ORDER BY RANDOM()

--Survival user
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Survival%'
and not gr.critic_or_not
ORDER BY RANDOM()

--Racing critic
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Racing%'
and gr.critic_or_not
ORDER BY RANDOM()

--Racing user
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Racing%'
and not gr.critic_or_not
ORDER BY RANDOM()

--Fighting critic
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Fighting%'
and gr.critic_or_not
ORDER BY RANDOM()

--Fighting user
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and gi.genres like '%Fighting%'
and not gr.critic_or_not
ORDER BY RANDOM()

--Sports critic 
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and (gi.genres like '%Soccer%' OR gi.genres like '%Football%' OR gi.genres like '%Basketball%' or gi.genres like '%Tennis%' or gi.genres like '%Baseball%' or gi.genres like '%Sport%' or gi.genres like '%Biking%')
and gr.critic_or_not
ORDER BY RANDOM()

--Sports user
select review, score
from game_review as gr, game_info as gi
where gr.game = gi.title 
and (gi.genres like '%Soccer%' OR gi.genres like '%Football%' OR gi.genres like '%Basketball%' or gi.genres like '%Tennis%' or gi.genres like '%Baseball%' or gi.genres like '%Sport%' or gi.genres like '%Biking%')
and not gr.critic_or_not
ORDER BY RANDOM()