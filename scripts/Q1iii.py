#String which returns an acronym for a phrase

def get_acronym(phrase):
    words = phrase.split(' ')
    print(words)
    initials = []
    for w in words:
        initials.append(w[0].upper())
    result = ''.join(initials)
    print(result)

get_acronym('the cat jumps over the dog')