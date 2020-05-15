create table input_file(line string);

create external table input_file(line string) 
location '/user/bigdata17/input_files/';

create table words as
select regexp_replace(input_file.line, '[^0-9A-Za-z ]+', '') as line
from input_file;

create table word_count as
select word, count(1) as count from
(SELECT explode(split(line, '\\s+')) AS word FROM words) w
group by word
order by word;

select * from word_count where word != ''  order by count desc limit 100;
select * from word_count where length(word_count.word) >= 6 order by count desc limit 100;
