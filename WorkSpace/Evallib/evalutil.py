# this library is ued to make evaluation of ranked list
import numpy as np
import pandas as pd
import psycopg2
import pickle

# loading global variables
print("Start evaluation data loading...")

# load game infomations
all_games = pd.read_csv("data/all_game.csv")
all_games = all_games["game_name"].values.tolist()
all_games_set = set(all_games)
total_game_count = len(all_games)
print("game information loaded.")
print(f"total game count: {total_game_count}")

# load user list
with open('data/user_list.pickle', 'rb') as f:
    user_list = pickle.load(f)
# number of user: 147402, train dataset index 0 - 9999 (10,000), evaluation dataset index 20000 - 119999 (100,000)
eval_user_list = user_list[20000:120000].copy()
eval_user_list.sort()
print("user information loaded.")
print(f"total users: {len(eval_user_list)}")

# load user reviews
with open('data/eval_reviews.pickle', 'rb') as f:
    eval_reviews = pickle.load(f)
print("user reviews loaded.")
total_reviews = 0
for user in eval_user_list:
    total_reviews += len(eval_reviews[user])
print(f"total reviews count: {total_reviews}" )

def get_games():
    return all_games_set

def single_user_evaluation(user_records, ranking, top_n=100, decay=1.0):
    """
        user_records: the review entities of the user
        ranking: ordered list of rank of product
        top_n: only consider the top n games in the ranking list
        decay: the score (in many format) decay rate compared with previous item, (e.g. 1st item get 100% score, 2nd get 100% * decay, and 3rd get 100% * decay^2 ...)
    """

    if set(ranking) != all_games_set:
        raise Exception("the ranking is not in correct format!")
    
    positive_count = 0.0
    negative_count = 0.0
    positive_playing_hours = 0.0
    negative_playing_hours = 0.0
    
    for r in user_records:
        game_name = r[0]
        rank_pos = ranking.index(game_name)
        if rank_pos < top_n:
            if r[1]:
                positive_count += 1.0 * (decay ** rank_pos)
                positive_playing_hours += r[2] * (decay ** rank_pos)
            else:
                negative_count += 1.0 * (decay ** rank_pos)
                negative_playing_hours += r[2] * (decay ** rank_pos)
    
    total_purchase_number = positive_count + negative_count
    total_playing_hours = positive_playing_hours + negative_playing_hours

    return [
        total_purchase_number,
        total_playing_hours,
        positive_count,
        negative_count,
        positive_playing_hours,
        negative_playing_hours,
        positive_count/(total_purchase_number + 0.0000001), # prevent divide by 0
        negative_count/(total_purchase_number + 0.0000001),
        positive_playing_hours/(total_playing_hours + 0.0000001),
        negative_playing_hours/(total_playing_hours + 0.0000001)
    ]

def evaluation(ranking, top_n=100, decay=1.0):
    """
        this function will calculate evaluation results by averaging of the 100,000 users
    """
    results = []
    for u in eval_reviews.keys():
        results.append(single_user_evaluation(eval_reviews[u], ranking=ranking, top_n=top_n, decay=decay))
    results = np.array(results)
    return results

