import string
from divide_lines import replace_invalid_chars
from divide_lines import process_line
from collections import Counter


def test_replace_invalid_chars_no_special_char_reserved():
    test_string = '@#$%!@#$%!@#%#$%$#%!@#%!@#$@#.,,.,.,.abcd'
    output_string = replace_invalid_chars(test_string)

    for char in output_string:
        assert char in set(string.ascii_letters) or char == ' '


def test_replace_invalid_chars():
    test_string = 'a,b.c?d.e '
    output_string = replace_invalid_chars(test_string)
    assert output_string == 'a b c d e '


def test_process_line():
    word_count = Counter()
    test_string = 'happy!@#!@sad!@#!@happy,,,...  sad   sad sadsad happy@!#@#'
    process_line(test_string, word_count)
    assert word_count['happy'] == 3
    assert word_count['sad'] == 3
    assert word_count['sadsad'] == 1


test_replace_invalid_chars_no_special_char_reserved()
test_replace_invalid_chars()
test_process_line()

print('All Testing done')



