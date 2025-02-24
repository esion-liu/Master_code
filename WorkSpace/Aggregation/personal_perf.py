# this file is used for personal preference generation based on pair-wise comprisions
import random
import functools

def prefernce_generation(pairs) -> list:
    """
    parameters:
        pairs format list of tuples, e.g. [('GTA', 'CSGO'), ('CSGO', 'StarCraft'), ('GTA', 'StarCraft')]
        where 1st item is prefered to 2nd item in each tuple.
        lack of pair tuple means an indifference between two alternatives
    return:
        a list represent the preference order of the user, e.g. ['GTA', 'CSGO', 'StarCraft']
    """

    alter_counter = dict()
    for i in pairs:
        if i[0] not in alter_counter.keys():
            alter_counter[i[0]] = 0.0
        if i[1] not in alter_counter.keys():
            alter_counter[i[1]] = 0.0

    alternatives = list(alter_counter.keys())

    for i in range(len(alternatives) - 1):
        for j in range(i+1, len(alternatives)):
            if (alternatives[i], alternatives[j]) in pairs:
                alter_counter[alternatives[i]] += 1
            elif (alternatives[j], alternatives[i]) in pairs:
                alter_counter[alternatives[j]] += 1
            else:
                alter_counter[alternatives[i]] += 0.5
                alter_counter[alternatives[j]] += 0.5
    
    def custom_compare(a, b):
        if alter_counter[a] > alter_counter[b]:
            return 1
        elif alter_counter[a] < alter_counter[b]:
            return -1
        elif (a, b) in pairs:
            return 1
        elif (b, a) in pairs:
            return -1
        else:
            return 0
        
    sorted_alter = sorted(alternatives, key=functools.cmp_to_key(custom_compare))
    sorted_alter.reverse()

    return sorted_alter


def merge_sort_preference_generation(pairs) -> list:
    """
    parameters:
        pairs format list of tuples, e.g. [('GTA', 'CSGO'), ('CSGO', 'StarCraft'), ('GTA', 'StarCraft')]
        where 1st item is prefered to 2nd item in each tuple.
        lack of pair tuple means an indifference between two alternatives
    return:
        a list represent the preference order of the user, e.g. ['GTA', 'CSGO', 'StarCraft']
    This function simulate an O(nlog(n)) solution, which is more time efficient but less accurate
    """

    alternatives = []
    for i in pairs:
        if i[0] not in alternatives:
            alternatives.append(i[0])
        if i[1] not in alternatives:
            alternatives.append(i[1])
    
    random.shuffle(alternatives)

    def merge_sort(arr, cmp):
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left_half = merge_sort(arr[:mid], cmp)
        right_half = merge_sort(arr[mid:], cmp)

        return merge(left_half, right_half, cmp)
    
    def merge(left, right, cmp):
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if cmp(left[i], right[j]) <= 0:  # Use the custom comparison function
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        
        return result
    
    def custom_compare(a, b):
        if (a, b) in pairs:
            return 1
        elif (b, a) in pairs:
            return -1
        else:
            return 0
        
    sorted_list = merge_sort(alternatives, custom_compare)
    sorted_list.reverse()

    return sorted_list


def quick_sort_preference_generation(pairs) -> list:
    """
    parameters:
        pairs format list of tuples, e.g. [('GTA', 'CSGO'), ('CSGO', 'StarCraft'), ('GTA', 'StarCraft')]
        where 1st item is prefered to 2nd item in each tuple.
        lack of pair tuple means an indifference between two alternatives
    return:
        a list represent the preference order of the user, e.g. ['GTA', 'CSGO', 'StarCraft']
    This function simulate an O(nlog(n)) solution, which is more time efficient but less accurate
    """

    alternatives = []
    for i in pairs:
        if i[0] not in alternatives:
            alternatives.append(i[0])
        if i[1] not in alternatives:
            alternatives.append(i[1])
    
    random.shuffle(alternatives)

    def quick_sort(arr, cmp):
        if len(arr) <= 1:
            return arr

        pivot = arr[len(arr) // 2]
        less = [x for x in arr if cmp(x, pivot) < 0]  # Elements less than pivot
        equal = [x for x in arr if cmp(x, pivot) == 0]  # Elements equal to pivot
        greater = [x for x in arr if cmp(x, pivot) > 0]  # Elements greater than pivot

        return quick_sort(less, cmp) + equal + quick_sort(greater, cmp)
    
    def custom_compare(a, b):
        if (a, b) in pairs:
            return 1
        elif (b, a) in pairs:
            return -1
        else:
            return 0
        
    sorted_list = quick_sort(alternatives, custom_compare)
    sorted_list.reverse()

    return sorted_list