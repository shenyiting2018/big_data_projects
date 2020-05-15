#!/usr/bin/python
# This is the first reducer that will be used for the top 100 words soring
# The job of this reducer is to aggregate word count
import itertools
import operator
import sys

from itertools import groupby



current_word = None
current_count = 0
word = None


def read_mapper_output(file):
    for line in file:
        # strip out whitespaces and lazy load
        yield line.strip().split('\t', 1)


def main():
    data = read_mapper_output(sys.stdin)
    # Read data through standard input stream
    # Group by the data's first element, which is the word
     for current_word, group in itertools.groupby(data, operator.itemgetter(0)):
        try:
            total_count = sum(int(count) for current_word, count in group)
            print("{}{}{}".format(current_word, ' ', total_count))
        except ValueError:
            # if the word is not valid, ignore it
            pass


if __name__ == "__main__":
    main()