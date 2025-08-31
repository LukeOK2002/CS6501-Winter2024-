#Write a python function 'max_gap(n)' which simulates n number of dice rolls and returns the maximum distance between 6s in each simulation
#Write a function 'analyze_gap(m, n)' which simulates m number of dice rolls of n length and returns the mode value

import random

def max_gap(n):
    # Generating a list of dice rolls
    run = [random.randint(1, 6) for roll in range(n)]

    # Getting a list of positions where 6 appears
    position_list = [i for i, val in enumerate(run) if val == 6]

    #Determining the gaps between the 6s
    gap = []
    for position_index in range(len(position_list) - 1):
        #Getting the distance between each gap, multiplying by -1 as value is always negative
        gap.append(-1 * (position_list[position_index] - position_list[position_index + 1]))
    #Returning highest gap value, have to add an exception if there isn't a gap

    gap_result = max(gap) if gap else None

    print(gap_result)
    return gap_result





def analyze_gaps(n, m):
    max_gaps = [max_gap(n) for _ in range(m)]
    print(max_gaps)
    #Getting rid of None answers so that max(valid_gaps) doesn't throw an error
    valid_gaps = [gap for gap in max_gaps if gap is not None]
    most_common = {}
    for i in valid_gaps:
        most_common[i] = most_common.get(i, 0) + 1

    if most_common:
        max_count = max(most_common.values())
        mode_gaps = [gap for gap, count in most_common.items() if count == max_count]
        #Decided to convert the numbers list into a string so it can be presented better
        gaps_as_string = [str(element) for element in mode_gaps]
        if len(mode_gaps) > 1:
            print(f'The most common gap lengths are {", ".join(gaps_as_string)}')
        else:
            print(f'The most common gap length is {gaps_as_string[0]}')

analyze_gaps(10, 10)