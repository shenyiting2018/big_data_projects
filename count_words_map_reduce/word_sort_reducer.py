#!/usr/bin/python
# This is the second reducer that will be used for the top 100 words soring
# The job of this reducer is to do sorting

import itertools
import operators
import sys


def read_mapper_output(file):
    for line in file:
        yield line.strip().split('\t', 1)


def main():
    data = read_mapper_output(sys.stdin)
    for current_count, group in itertools.groupby(data, operators.itemgetter(0)):
        try:
            words = [word for count, word in group]
            print("%s%s%d" % (current_count, '\t', str(words)))
        except ValueError:
            # count invalid, ignore it
            pass


if __name__ == "__main__":
    main()


