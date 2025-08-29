#Write a function 'coinflips' that simulates coinflips until the first occurence of two heads
#Print the string of coinflips and return the length

import random

def coinflips():
    flip_string = ''
    while 'HH' not in flip_string:
        flip = random.randint(0,1)
        if flip == 0:
            flip_string += 'H'
        else:
            flip_string += 'T'
    print(flip_string)
    #Question says to _return_ the length, but never gets output
    return len(flip_string)

coinflips()