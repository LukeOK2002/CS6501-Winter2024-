#Write a function undulate(fname) that opens a text file titled fname.txt, the words in the text file should undulate between uppercase and lowercase
#The case of the start of each word should remain unchanged
#For full marks, leave all punctuation intact
import re

def undulate(fname):
    new_string = ''
    word_list = fname.split(' ')
    print(word_list)
    for word in word_list:
        temp_word = ''

        for i, letter in enumerate(word):
            #First letter retains original case
            if i == 0:
                temp_word += letter
            else:
                #Indexing previous position, checking if its upper or lower
                if temp_word[i - 1].isupper():
                    temp_word += letter.lower()
                else:
                    temp_word += letter.upper()

        new_string += temp_word + ' '

    return new_string






def main():
    with open(r"C:\Users\lisbo\Downloads\fname.txt") as input_data:
        fname = input_data.read().strip()
        output = undulate(fname)
    with open(r"C:\Users\lisbo\Downloads\fname_output.txt", "w") as output_data:
        output_data.write(output)

main()