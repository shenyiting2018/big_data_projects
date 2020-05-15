#!/usr/bin/python

# This is the second reducer that will be used for the top 100 words soring
# The job of this reducer is to do sorting

import sys

from itertools import groupby
from operator import itemgetter


def read_mapper_output(file):
    for line in file:
        yield line.rstrip().split('\t', 1)


def main():
    data = read_mapper_output(sys.stdin)
    # group by count
    for current_count, group in groupby(data, itemgetter(0)):
        try:
            words = [word for count, word in group]
            print("%s%s%s" % (current_count, '\t', str(words)))
        except ValueError:
            # count invalid, ignore it
            pass


if __name__ == "__main__":
    main()


