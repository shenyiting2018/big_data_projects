#!/usr/local/bin/python3

import argparse
import datetime

from pyspark import SparkConf, SparkContext
from prettytable import PrettyTable


def generate_rdds(movie_file, review_file, spark_context):
    # generate rdds for reviews/movies
    reviews = spark_context.textFile(review_file)
    movies = spark_context.textFile(movie_file)

    # Filter header
    reviews_header = reviews.first()
    reviews = reviews.filter(lambda review: review != reviews_header)
    movies_header = movies.first()
    movies = movies.filter(lambda movie: movie != movies_header)

    # We don't need the timestamp field, so filter it out
    movies = movies.map(lambda movie: (int(movie.split(',')[0]), (movie.split(',')[1:-1])))

    # each entry has such structure: user_id,movie_id,rating,timestamp
    # we map the entire entry to : movie_id, 1
    movie_reviews = reviews.map(lambda review: (int(review.split(',')[1]), 1))
    movie_ratings = reviews.map(lambda review: (int(review.split(',')[1]), float(review.split(',')[2])))

    # For all the entries with same key, aka, movie_id, sum up their count
    movie_review_counts = movie_reviews.reduceByKey(lambda x, y: x + y)
    movie_rating_sums = movie_ratings.reduceByKey(lambda x, y: x + y)

    # join the three rdds
    movies = movies.join(movie_rating_sums).join(movie_review_counts)

    movies_tuple = movies.map(
        lambda movie: (
            movie[0],  # first el: movie_id
            (   # second el: movie_name, movie_total_rating, movie_review_count
                ','.join(movie[1][0][0]).replace("\"", ''),
                movie[1][0][1] / movie[1][1],
                movie[1][1],
            )
         )
    )

    return movies_tuple


def complete_task_1(movies_tuple, k):
    # example of movies_tuple:
    # (6, ('Heat (1995)', 4.1412313, 104))
    most_popular_movies = movies_tuple.map(
        lambda movie: (movie[1][2], (movie[0], movie[1][0], movie[1][1], movie[1][2]))
    ).sortByKey()

    # Grep top 10
    most_popular_movies = most_popular_movies.collect()[-1:-(k + 1):-1]

    t = PrettyTable()
    t.title = "Top {} Movies".format(k)
    t.field_names = ["Ranking", "Movie ID", "Movie Name", "Movie Rating", "Number of Reviews"]
    ranking = 1
    for _, (movie_id, movie_name, movie_rating, count_of_reviews) in most_popular_movies:
        t.add_row([ranking, movie_id, movie_name, "{:.1f}".format(movie_rating), count_of_reviews])
        ranking += 1
    print(t)


def complete_task_2(movies_tuple):
    filtered_movies_tuple = movies_tuple.filter(
        lambda movie: movie[1][1] > 4.0 and movie[1][2] > 10
    ).sortByKey()

    movies = filtered_movies_tuple.collect()
    t = PrettyTable()
    t.title = "Movies"
    t.field_names = ["Movie ID", "Movie Name", "Rating", "Number of Reviews"]
    for movie_id, (movie_name, movie_rating, number_of_reviews) in movies:
        t.add_row([movie_id, movie_name, "{:.1f}".format(movie_rating), number_of_reviews])
    print(t)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-file", help="The input file of reviews")
    parser.add_argument("--movie-file", help="The input file of movies")
    parser.add_argument("--task-2", action="store_true", help="For task 2")
    parser.add_argument("--K", "-k", help="Number of top K words")
    parser.add_argument("--t")
    parser.add_argument("--tuning", action="store_true")
    args = parser.parse_args()

    review_file = args.review_file
    movie_file = args.movie_file
    is_task_2 = args.task_2
    k = args.K or 10
    k = int(k)
    t = args.t
    tuning = args.tuning

    threads = []
    if tuning:
        threads = [1, 2, 3, 5, 8, 13]
    else:
        threads = [t if t else 1]

    for thread in threads:
        master = 'local[{}]'.format(thread)

        conf = SparkConf().setMaster(master).setAppName("MovieRanking")
        spark_context = SparkContext(conf=conf)

        print('spark conf: {}'.format(str(spark_context.getConf().getAll())))

        time_start = datetime.datetime.now()
        movies_tuple = generate_rdds(movie_file, review_file, spark_context)

        if is_task_2:
            complete_task_2(movies_tuple)
        else:
            complete_task_1(movies_tuple, k)

        time_end = datetime.datetime.now()
        print('threads:{}, duration: {}'.format(thread, time_end - time_start))
        # SparkContext.stop(spark_context)
        spark_context.stop()


if __name__ == "__main__":
    main()
