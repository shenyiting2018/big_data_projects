#!/usr/bin/env python

import tweepy
from tweepy.auth import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import socket
import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import sys

CONSUMER_KEY = "W8oUM1PbgLO9HYUaKGyPvneHx"
CONSUMER_SECRET_KEY = "xexZIKTxFngvwMjbNgR3QhHgbrCIiDqArKQaJj5x0D1xyhLpJM"
ACCESS_TOKEN = "1199365855257038849-wWN4zOVl6Jv0A6dTOM0R91Y1OA5gyS"
ACCESS_TOKEN_SECRET = "d8AOVHRS1IWeYpgHVLtlHBQDG22m67rwpCfbk6hIgMYaf"


class TweetsListener(StreamListener):
    def __init__(self, csocket):
        self.client_socket = csocket

    def on_data(self, data):
        try:
            message = json.loads(data)
            print(message['text'].encode('utf-8'))
            self.client_socket.send(message['text'].encode('utf-8'))
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def if_error(self, status):
        print(status)
        return True

def send_tweets(c_socket):
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    twitter_stream = Stream(auth, TweetsListener(c_socket))
    #twitter_stream.filter(track=)


if __name__=="__main__":
    new_skt = socket.socket()
    host = "127.0.0.1"
    port = 9999
    new_skt.bind((host, port))

    print("Listening on port: %s" % str(port))

    new_skt.listen(5)
    c, addr = new_skt.accept()

    print("Accept the request from " + str(addr))

    send_tweets(c)



