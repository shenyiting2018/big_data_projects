import string
import time
from collections import Counter
import heapq

K = 10
word_counter = Counter()
filename = "./dataset-400MB.txt"
valid_chars = set(string.ascii_letters)
CHUNK_SIZE = 10000
timestamps = []

current_milli_time = lambda: int(round(time.time() * 1000))

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

count = 0


with open(filename) as f:
    while True:
        line = f.readline()
        if not line:
            break
        process_line(line, word_counter)
        count += 1
        if count % CHUNK_SIZE == 0:
            timestamps.append(current_milli_time())
            print(count)

with open('word_counts.out', 'w') as f:
    f.write(str(word_counter))


with open('velocity.out', 'w') as f:
    f.write(str(timestamps))


# start counting
heap = []
for word, count in word_counter.items():
    if len(heap) < K:
        heapq.heappush(heap, (count, word))
    else:
        heapq.heappushpop(heap, (count, word))


while heap:
    print(heapq.heappop(heap))



    # for lines in read_in_chunks(f):
    #     process_line(lines, word_counter)


# with open(filename) as f:
#     pass
#
# while 1:
#     #lines = file.readlines(100000)
#     if not lines:
#         break
#     for line in lines:
#         process_line(line)
#     count += 100000
#     print(count)
    
# for i in range(len(items) - 1, len(items) - K - 1, -1):
#     print(items[i][1] + "\t" + str(items[i][0]))




