def substring(sequences):
    shortest = min(sequences, key=len)
    longest = ""

    for i in range(len(shortest)):
        for j in range(i+1, len(shortest)+1):
            candidate = shortest[i:j]
            if len(candidate) > len(longest) and all(candidate in seq for seq in sequences):
                longest = candidate
    print(longest)
    return longest

def main():
    sequences = []
    current_sequence = []

    with open(r"C:\Users\lisbo\Downloads\rosalind_lcsm.txt") as input_data:
        for line in input_data:
            line = line.strip()
            if line.startswith('>'):
                if current_sequence:
                    sequences.append("".join(current_sequence))
                    current_sequence = []
            else:
                current_sequence.append(line)

        if current_sequence:
            sequences.append("".join(current_sequence))
    motif = substring(sequences)
    print(motif)
    return sequences





main()

