import tweepy
import json

f = open('twitter.json')
bearer_token = json.load(f)["bearer"]
client = tweepy.Client(bearer_token)
object_methods = [method_name for method_name in dir(client)
                  if callable(getattr(client, method_name))]
