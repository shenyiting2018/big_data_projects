#!/usr/bin/python

import string
import sys


# Define the valid char set
valid_chars = set(string.ascii_letters)


def replace_invalid_chars(line):
    # Java string buffer like structure
    converted_output = []
    for character in line:
        if character in valid_chars or character == '\s':
            converted_output.append(character)
        else:
            converted_output.append(' ')
    return ''.join(converted_output)


def read_input(file):
    for line in file:
        line = replace_invalid_chars(line)
        # yield each line to enable lazy load
        yield line.split()

def main(separator = '\t'):
    data = read_input(sys.stdin)
    for words in data:
        for word in words:
            print ('%s%s%d' % (word, separator, 1))


if __name__ == "__main__":
    main()