#!/usr/local/bin/python3

import string
import time
import heapq
import statistics
import sys
import os
import argparse
from collections import Counter
import datetime
import psutil


valid_chars = set(string.ascii_letters)


def current_milli_time(): return int(round(time.time() * 1000))


def replace_invalid_chars(line):
    converted_output = []
    for character in line:
        if character in valid_chars or character == '\s':
            converted_output.append(character)
        else:
            converted_output.append(' ')
    return ''.join(converted_output)


def process_line(line, word_counter):
    line = replace_invalid_chars(line)
    words = line.split()
    for word in words:
        word_counter[word] += 1


def main():
    # Define and process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", "--filename", help="The input file name")
    parser.add_argument("--K", "--K", help="The top K word counts, default is 10")
    parser.add_argument("--chunk-size", "--chunk_size",
                        help="The chunk size for time granualarity, default is 10000")
    parser.add_argument("--debug", "--debug", action="store_true", help="Enter debug mode")
    parser.add_argument("--total-lines", "--total_lines", help="help tracking progress")
    args = parser.parse_args()

    if not args.filename:
        raise ValueError("Filename must be provided")

    K = int(args.K) if args.K else 10
    filename = args.filename
    chunk_size = int(args.chunk_size) if args.chunk_size else 100000
    word_counter = Counter()
    timestamps = []
    velocity = []
    count = 0
    debug = bool(args.debug)
    cpu_usages = []
    mem_usages = []
    total_lines = int(args.total_lines) if args.total_lines else None

    final_output_and_analysis_filename = 'final_output_and_analysis-{}.txt'.format(filename.replace('.txt', ''))
    word_counts_output_filename = 'word_counts-{}.debug'.format(filename.replace('.txt', ''))
    velocity_output_filename = 'velocity-per-{}-{}.debug'.format(chunk_size, filename.replace('.txt', ''))
    mem_usages_output_filename = 'mem-usages-{}.debug'.format(filename.replace('.txt', ''))
    cpu_usages_output_filename = 'cpu-usages-{}.debug'.format(filename.replace('.txt', ''))


    # log timestamps
    start_processing_time = datetime.datetime.now()
    start_processing_timestamp = current_milli_time()
    process = psutil.Process(os.getpid())

    start_logline = "Start processing at {}. pid: {}".format(str(start_processing_time), process)
    print(start_logline)



    # Open file and start processing
    with open(filename) as f:
        prev_timestamp = current_milli_time()
        while True:
            line = f.readline()
            if not line:
                break

            process_line(line, word_counter)

            count += 1
            if count % chunk_size == 0:
                current_timestamp = current_milli_time()
                timestamps.append(current_timestamp)
                velocity.append(current_timestamp - prev_timestamp)
                prev_timestamp = current_timestamp
                mem_usages.append(process.memory_info().rss)
                cpu_usages.append(process.cpu_percent())

                if debug:
                    print(
                        "Processed {} lines of text. Took {} milliseconds for this chunk. Memory usage: {} KB, CPU usage:{}. Current progress: {}".format(
                            count,
                            velocity[-1],
                             mem_usages[-1],
                             cpu_usages[-1],
                             "{0:.0%}".format(count / total_lines) if total_lines else 'NaN'
                             ),
                        )


    # File processing finished, log timestamp
    complete_processing_time = datetime.datetime.now()
    complete_processing_timestamp = current_milli_time()
    complete_logline = "Finish processing at {}. Processing file took {} seconds. Size of word counter dictionary: {}".format(
        str(complete_processing_time),
        (complete_processing_timestamp - start_processing_timestamp) // 1000,
        sys.getsizeof(word_counter)
    )
    print(complete_logline)

    # start sorting
    sorting_processing_time = datetime.datetime.now()
    sorting_processing_timestamp = current_milli_time()
    start_sorting_logline = "Start sorting at {}".format(str(sorting_processing_time))
    print(start_sorting_logline)

    heap = []
    for word, count in word_counter.items():
        if len(heap) < K:
            heapq.heappush(heap, (count, word))
        else:
            heapq.heappushpop(heap, (count, word))

    # Finished sorting
    sorting_complete_processing_time = datetime.datetime.now()
    sorting_complete_processing_timestamp = current_milli_time()
    complete_sorting_logline = "Finish sorting at {}. Sorting word counters took {} milliseconds. Size of heap to sorting is: {}".format(
        str(sorting_complete_processing_time),
        (sorting_complete_processing_timestamp - sorting_processing_timestamp),
        sys.getsizeof(heap),
    )
    print(complete_sorting_logline)

    # Starting writing down lines
    with open(final_output_and_analysis_filename, 'w') as f:
        init_lines_analysis_file ="""
Final counting words result for {0}'.
------------------------------------------------------
Event timestamps:
{1}
{2}
{3}
{4}
------------------------------------------------------
Performance:
max_cpu_usage: {5}
average_cpu_usage: {6}
median_cpu_usage: {7}
max_memory_usage: {8}
average_memory_usage: {9}
median_memory_usage: {10}
word_count_dictionary_size: {11}
heap_size: {12}
------------------------------------------------------
Top {13} words and counts:
""".format(
    filename,
    start_logline,
    complete_logline,
    start_sorting_logline,
    complete_sorting_logline,
    max(cpu_usages),
    statistics.mean(cpu_usages),
    statistics.median(cpu_usages),
    max(mem_usages),
    statistics.mean(mem_usages),
    statistics.median(mem_usages),
    sys.getsizeof(word_counter),
    sys.getsizeof(heap),
    K,
)
        print(init_lines_analysis_file)
        f.write(init_lines_analysis_file)

        top_words = []
        while heap:
            count, word=heapq.heappop(heap)
            top_words.append((word, count))

        for word, count in top_words[::-1]:
            line = "Word: {}, count: {}".format(word, count)
            print(line)
            f.write(line + "\n")


    if debug:
        with open(word_counts_output_filename, 'w') as f:
            f.write(str(word_counter))

        with open(velocity_output_filename, 'w') as f:
            f.write(str(velocity))

        with open(mem_usages_output_filename, 'w') as f:
            f.write(str(mem_usages))

        with open(cpu_usages_output_filename, 'w') as f:
            f.write(str(cpu_usages))


if __name__ == "__main__":
    main()
