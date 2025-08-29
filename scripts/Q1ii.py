#Write a function 'diagonal' that prints an nxn pattern in which points on or
#below the main diagonal appear as dots and those above appear as hash marks


def diagonal(n):
    table_length = n - 1
    while table_length > 0:
        for i in range(table_length):
            string = ((n - table_length) * ('.')) + table_length*'#'
            table_length -= 1
            print(string)

diagonal(8)

