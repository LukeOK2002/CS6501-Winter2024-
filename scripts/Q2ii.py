#Write a function called 'unique_characters(s) that analyses a string and outputs the number of unique characters
#contained within e.g 'Hello World' would have ten and 'xxx' one, use a dictionary to solve this problem

def unique_characters(s):
    dictionary = {}
    for character in s:
        if character not in dictionary:
            dictionary[character] = 1
    print(len(dictionary))

unique_characters('grass')