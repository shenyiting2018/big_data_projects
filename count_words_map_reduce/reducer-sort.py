#!/usr/bin/python

import sys
from itertools import groupby
from operator import itemgetter

word_list = []

def read_mapper_output(file, separator='\t'):
    for line in file:
        yield line.rstrip().split(separator, 1)


def main(separator='\t'):
    data = read_mapper_output(sys.stdin, separator=separator)
    #input comes from STDIN
    for current_count, group in groupby(data, itemgetter(0)):
        try:
            words = [word for count, word in group]
            print("%s%s%s" % (current_count, separator, str(words)))
        except ValueError:
            # count was not a number, so silently discard this item
            pass


if __name__ == "__main__":
    main()


