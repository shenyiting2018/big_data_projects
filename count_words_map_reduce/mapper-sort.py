#!/usr/bin/python

import sys

def read_dictionary(file):
    for line in file:
        yield line.split()

def main(separator = '\t'):
    data = read_dictionary(sys.stdin)
    for word, count in data:
        print ('{}{}{}'.format(count, separator, word))


if __name__ == "__main__":
    main()