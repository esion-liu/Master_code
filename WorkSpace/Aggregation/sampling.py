# this file contains sampling algorithms that can generate full ballots based on distorted ballot
import random
import pandas as pd
import numpy as np
import time

# load the list of all games
all_games = pd.read_csv("data/all_game.csv")
all_games = all_games["game_name"].values.tolist()
print("game list loaded")

# to save space, will create an index for games, so that each title will have a unique intiger index
# thus, the index in list all_games will be used

def index_convertion(distorted_ballot, index_list=all_games):
    result = []
    for i in distorted_ballot:
        result.append(index_list.index(i))
    return result

# for group index convertion
def index_convertion_profile(profile, index_list=all_games):
    result = []
    for p in profile:
        result.append(index_convertion(p, index_list))
    return result

# function for reverse convertion
def title_convertion(indexed_distorted_ballot, index_list=all_games):
    result = []
    for i in indexed_distorted_ballot:
         result.append(index_list[i])
    return result

# group reversee convertion
def title_convertion_progile(profile, index_list=all_games):
    result = []
    for p in profile:
        result.append(title_convertion(p, index_list))
    return result

def personal_perf_sampling(distorted_ballot, alternative_number=len(all_games), gamma=1.0, sample_number=1):
    """
    params:
        distort_ballot: indexed distorted ballot
        alternative_number: number of alternatives
        gamma: used for adjusting of positions of items in distorted_ballot
        sample_number: number of samples for generation
    """
    result = []
    full_alternatives = list(range(alternative_number))

    for _ in range(sample_number):
        ballot_rand_util = sorted([random.random() ** gamma for _ in range(len(distorted_ballot))], reverse=True)
        full_alt_util = []
        for alt in full_alternatives:
            if alt in distorted_ballot:
                full_alt_util.append({'alt': alt, 'utl': ballot_rand_util[distorted_ballot.index(alt)]})
            else:
                full_alt_util.append({'alt': alt, 'utl': random.random()})
        full_alt_util = sorted(full_alt_util, key=lambda x: x['utl'], reverse=True)
        result.append([alt['alt'] for alt in full_alt_util])

    return result

# used for sample genetion of a group of distorted ballots (distorted profile)
def profile_sampling(profile, alternative_number=len(all_games), gamma=1.0, sample_number=1):
    result = []
    for p in profile:
        result = result + personal_perf_sampling(p, alternative_number, gamma, sample_number)
    return result

# -----------------------------------------------------------------------------------------------------------

def order_generation(util_list):
    temp_list = util_list.copy()
    temp_list = sorted(temp_list, reverse=True)
    result = [util_list.index(i) for i in temp_list]
    return result

def random_normal_distribution(mean=0, std=1) -> float:
    return float(np.random.normal(mean, std, 1)[0])

# RUM_sampling
def RUM_sampling(ballot, alternative_number=len(all_games), sample_number=1):
    result = []
    full_alternatives = list(range(alternative_number))

    for _ in range(sample_number):
        ballot_rand_util = sorted([random_normal_distribution() for _ in range(len(ballot))], reverse=True)
        full_alt_util = []
        for alt in full_alternatives:
            if alt in ballot:
                full_alt_util.append(ballot_rand_util[ballot.index(alt)])
            else:
                full_alt_util.append(random_normal_distribution())
        result.append(full_alt_util)
    return result

# RUM resampling
def RUM_resampling(grand_parent_ballot, parent_sample, sample_number, resample_rate=0.5, resample_step=1.0):
    """
    resample means generate offspring of a sample
    params:
        grand_parent_ballot: purpose is to make sure utility of alts in distorted ballot ranked decresingly
        parent_sample: resample template
        sample_number: number of resample offspring instances to be generated
        resample_rate: percentage of alt'utilities need to be changed
        resample_step: can be viewed as the parameter to adjust differences between parent_sample and child_sample
    """
    alternative_number = len(parent_sample)
    full_alternatives = list(range(alternative_number))

    # utility for alternatives appears in grand_parent_ballot
    grand_util = []
    for alt in grand_parent_ballot:
        grand_util.append(parent_sample[alt])
    
    result = []
    for _ in range(sample_number):
        resample_grand_util = grand_util.copy()
        for i in range(len(resample_grand_util)):
            if random.random() < resample_rate:
                resample_grand_util[i] = (resample_grand_util[i] + resample_step*random_normal_distribution()) / (1.0 + resample_step)
        resample_grand_util = sorted(resample_grand_util, reverse=True)
        full_alt_util = []
        for alt in full_alternatives:
            if alt in grand_parent_ballot:
                full_alt_util.append(resample_grand_util[grand_parent_ballot.index(alt)])
            else:
                if random.random() < resample_rate:
                    full_alt_util.append((parent_sample[alt] + resample_step*random_normal_distribution()) / (1.0 + resample_step))
                else:
                    full_alt_util.append(parent_sample[alt])
        result.append(full_alt_util)
    return result

# Log of Guassian Likelihood (base e)
def likeihood_guassian(observed, expected, std=0.3):
    log_constant = -0.5 * np.log(2 * np.pi * std**2)
    quadratic_term = -((observed - expected)**2)/(2 * std**2)
    return log_constant + quadratic_term

# the recursive sampling/resampling method for theta estimation
def theta_estimation(profile, alternative_number=len(all_games), iteration=100, sampling_rate=100, keep_rate=10, rand_alt_weight=0.1, resampling_rate=0.5, resampling_step=1.0, resampling_schedule=None, verbose=True):
    """
    params: 
        profile: list of lists, where inner lists represent each voter's preference order
        alternative_number: since profile contians distorted ballots, it is not sure that all alternatives are included in the profile
        iteratrion: number of iterations of resampling
        sampling_rate: number of samples generated from each distorted ballot
        keep_rate: in each resampling progress, keep keep_rate samples for each distorted ballot and regenerate sampling_rate - keep_rate samples
        rand_alt_weight: when calculate theta vector, alts appears in distorted ballot shold weighted more while random generated shouls weight less. Thus, alts in distorted ballot are weight 1.0, others weight this parameter.
        BE CAREFUL, the (sampling_rate - keep_rate) % keep_rate == 0 must hold for each keep sample generate equal number of new samples
    """
    start_time = time.time()

    # record some parameters during each iteration
    log = []

    # build resampling_schedule
    if resampling_schedule is None:
        resampling_schedule = []
        for i in range(iteration):
            resampling_schedule.append((resampling_rate, resampling_step))

    # generate origin set of samples
    num_voter = len(profile)
    temp = []
    for i in range(num_voter):
        temp += RUM_sampling(profile[i], alternative_number, sample_number=sampling_rate)
    sample_pool = np.array(temp)

    #generated weight matrix (alts in a ballot should weighted more than alts that did not appear in the ballot)
    temp = []
    for i in range(num_voter):
        for _ in range(sampling_rate):
            weight_row = [rand_alt_weight for _ in range(alternative_number)]
            for j in profile[i]:
                weight_row[j] = 1.0
            temp.append(weight_row)
    weight_matrix = np.array(temp)
    weights_sum = np.sum(weight_matrix, axis=0) 
    del temp

    # resampling for iteration times
    for iter in range(iteration):
        # calculate weighted sum for vector theta estimation
        weighted_sum = np.sum(sample_pool * weight_matrix, axis=0)
        theta = weighted_sum / weights_sum

        # each time making an estimation of theta, normalize it to make them normaly distributed with mean 0 and std 1
        theta_mean = np.mean(theta)
        theta_var = np.var(theta)
        theta = (theta - theta_mean) / np.sqrt(theta_var)

        # calculate log value of likelihood for each sample's each alternative
        likelihood_per_row_per_param = np.array([likeihood_guassian(sample_pool[:, i], theta[i]) for i in range(alternative_number)])
        likelihood_per_row_per_param = likelihood_per_row_per_param.transpose()

        ws = np.sum(likelihood_per_row_per_param * weight_matrix, axis=1)
        w = np.sum(weight_matrix, axis=1)

        likelihood_per_row = ws / w

        # average likelihood
        average_likelihood = np.sum(likelihood_per_row_per_param * weight_matrix) / np.sum(weight_matrix)

        # zeta (personal preference and noise) estimation (since personal_pref = theta + zeta, zeta = personal_pref - theta)
        # where personal_pref was estimated from samples

        '''
        zeta_estimation = []
        for i in range(num_voter):
            personal_samples = sample_pool[i*sampling_rate:(i+1)*sampling_rate]
            personal_pref = np.sum(personal_samples, axis=0)
            personal_pref = personal_pref / sampling_rate
            zeta_estimation.append((personal_pref - theta).tolist())
        zeta_estimation = np.array(zeta_estimation)

        log.append({
            "iteration": iter,
            "average_log_likelihood" : average_likelihood,
            "zeta_estimation": zeta_estimation,
            "theta_estimation": theta,
            "computation_time": (time.time() - start_time)
        })

        if verbose:
            print(f"iteration {iter}: average likelihood (log_value) is   {average_likelihood}") 
        '''

        keep_samples = []
        new_samples = []
        for i in range(num_voter):
            # keep high and likelihood and remove low likelihood samples for each origin distorted ballot
            personal_samples =  sample_pool[i*sampling_rate:(i+1)*sampling_rate].tolist()
            personal_sample_likelihood = likelihood_per_row[i*sampling_rate:(i+1)*sampling_rate].tolist()
            personal_sample_pairs = list(zip(personal_samples, personal_sample_likelihood))
            sorted_pairs = sorted(personal_sample_pairs, key=lambda x: x[1], reverse=True)
            personal_samples, _ = zip(*sorted_pairs)
            personal_samples = list(personal_samples)
            personal_samples = personal_samples[:keep_rate]
            keep_samples = keep_samples + personal_samples

            for j in range(len(personal_samples)):
                personal_samples += RUM_resampling(grand_parent_ballot=profile[i],
                                                   parent_sample=personal_samples[j],
                                                   sample_number=round((sampling_rate-keep_rate)/keep_rate),
                                                   resample_rate=resampling_schedule[iter][0],
                                                   resample_step=resampling_schedule[iter][1])
            
            new_samples += personal_samples

        # update sample pool
        random.shuffle(new_samples)
        sample_pool = np.array(new_samples)

        keep_samples = np.array(keep_samples)

        zeta_estimation = []
        for i in range(num_voter):
            personal_samples = keep_samples[i*keep_rate:(i+1)*keep_rate]
            personal_pref = np.sum(personal_samples, axis=0)
            personal_pref = personal_pref / keep_rate
            zeta_estimation.append((personal_pref - theta).tolist())
        zeta_estimation = np.array(zeta_estimation)

        log.append({
            "iteration": iter,
            "average_log_likelihood" : average_likelihood,
            "zeta_estimation": zeta_estimation,
            "theta_estimation": theta,
            "computation_time": (time.time() - start_time)
        })

        if verbose:
            print(f"iteration {iter}: average likelihood (log_value) is   {average_likelihood}")

    return log



