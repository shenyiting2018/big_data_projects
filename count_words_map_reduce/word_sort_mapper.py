#!/usr/bin/python
# This is the second mapper that will be used for the top 100 words soring
# The job of this mapper is to do sorting
import sys

def read_dictionary(file):
    for line in file:
    	# enable lazy load
      yield line.split()	

def main():
    data = read_dictionary(sys.stdin)
    for word, count in data:
        print("{}{}{}".format(count, ' ', word))


if __name__ == "__main__":
    main()