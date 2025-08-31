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

    print(run)
    print(position_list)
    print(gap)
    print(gap_result)
    return gap_result





def analyze_gaps(n, m):
    max_gaps = [max_gap(n) for _ in range(m)]
    print(max_gaps)
    #Getting rid of None answers so that max(valid_gaps) doesn't throw an error
    valid_gaps = [gap for gap in max_gaps if gap is not None]
    highest = max(valid_gaps)
    #Enumerating from max_gaps rather than valid_gaps
    winners = [i for i, g in enumerate(max_gaps) if g == highest]
    #Adding 1 as 'run number 0' doesn't sound very correct
    if len(winners) == 1:
        print(f'Winner is run number {winners[0] + 1} with highest gap {highest}')
    else:
        print(f'Its a tie! winners are runs number{winners + 1} with highest gap {highest}')








analyze_gaps(10, 10)