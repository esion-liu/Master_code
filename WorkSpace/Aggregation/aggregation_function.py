# this file will use the compsoc library for social preference (ranking list generation)
from compsoc.profile import Profile
from typing import Optional
import functools

# profile generation
def profile_generator(raw_profile: list, num_candidates: Optional[int], distorted=False) -> Profile:
    """
    generate compsoc standard Profile class from raw profile format which in the format of a list that contains each personal preference also in lists
    input format is list of lists, where inner lists represent prefernce orders of users
    Profile constructor input format: Profile({(17, (1,3,2,0)), (40, (3,0,1,2)), (52, (1,0,2,3))})
    where in (17, (1,3,2,0)) 17 is the number of identical ballot, while (1,3,2,0) is the preference order of 4 alternatives
    """

    counter = dict()
    for pref in raw_profile:
        tup = tuple(pref)
        if tup in counter.keys():
            counter[tup] = counter[tup] + 1
        else:
            counter[tup] = 1
    
    result = set()
    for ide_pref in counter.keys():
        result.add((counter[ide_pref], ide_pref))

    return Profile(result)
    

def aggregate(profile: Profile, voting_rule: callable) -> list:
    """
    in the composoc sdk, voting rule functions will take a profile and a candidate's index as input and output a "score" for this candidate.
    and candidates should rank with score decreasingly as generated social preference.
    """
    candidate_num = len(profile.candidates)
    candidates = list(range(candidate_num))
    scores = dict()

    for candidate in candidates:
        scores[candidate] = voting_rule(profile, candidate)
    
    def custom_compare(a, b):
        if scores[a] > scores[b]:
            return 1
        elif scores[a] < scores[b]:
            return -1
        else:
            return 0
        
    social_pref = sorted(candidates, key=functools.cmp_to_key(custom_compare))
    social_pref.reverse()

    return social_pref


def mixed_function_aggregate(profile: Profile, voting_rules: list, weights: list) -> list:
    """
    This function tooks a number of aggregation funcitons to build a mixed aggregation function, where the score of an alternative is weighted sum of these funcitons
    !!! One problem need consideration is that different functions give scores in a different range, for example functions give higher average scores will have more
    weight compared with funcitons which gaves lower average scores. to deal with this problem scores from each function will be first normalized then weighted summed
    """
    candidate_num = len(profile.candidates)
    candidates = list(range(candidate_num))
    all_scores = []

    for voting_rule in voting_rules:
        scores = dict()
        total_score = 0.0
        for candidate in candidates:
            scores[candidate] = voting_rule(profile, candidate)
            total_score += scores[candidate]
        for candidate in candidates:
            scores[candidate] = scores[candidate] / total_score
        
        all_scores.append[scores]
    
    final_scores = dict()

    for candidate in candidates:
        candidate_total_score = 0.0
        for i in range(len(all_scores)):
            candidate_total_score += all_scores[i][candidate] * weights[i]
        final_scores[candidate] = candidate_total_score
    
    def custom_compare(a, b):
        if final_scores[a] > final_scores[b]:
            return 1
        elif final_scores[a] < final_scores[b]:
            return -1
        else:
            return 0
    
    social_pref = sorted(candidates, key=functools.cmp_to_key(custom_compare))
    social_pref.reverse()

    return social_pref

        







