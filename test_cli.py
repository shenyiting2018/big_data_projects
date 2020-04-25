import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--filename", "--filename", help = "The input file name")
args = parser.parse_args()

if args.filename:
    print args.filename
