#!/usr/bin/python

# This is the first reducer that will be used for the top 100 words soring
# The job of this reducer is to do counting
import sys

from itertools import groupby
from operator import itemgetter


current_word = None
current_count = 0


def read_mapper_output(file):
    for line in file:
        yield line.rstrip().split('\t', 1)


def main():
    data = read_mapper_output(sys.stdin)
    # read input
    for current_word, group in groupby(data, itemgetter(0)):
        try:
            total_count = sum(int(count) for current_word, count in group)
            print("%s%s%d" % (current_word, '\t', total_count))
        except ValueError:
            # ignore invalid words
            pass


if __name__ == "__main__":
    main()