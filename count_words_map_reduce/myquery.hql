
create external table input_file(line string) 
location '/user/bigdata17/bigdata_input_files/';

create table words as
select regexp_replace(input_file.line, '[^0-9A-Za-z ]+', '') as line
from input_file;

create table word_count as
select word, count(1) as count from
(select explode(split(line, '\\s+')) as word from words) w
group by word;


select word, count from word_count where word != ''  order by count desc limit 100;

select word, count from word_count where length(word_count.word) > 6 order by count desc limit 100;

