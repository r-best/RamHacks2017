import googleapiclient.discovery
import tweepy
import json
import re
import datetime
import requests
import math

last_update = None
keys = None
twitter = None


def read_last_update_time():
    date_file = open('lastupdate.txt', 'r+')
    temp = re.split(' |-|:|\\.', date_file.readline())
    temp = [int(x) for x in temp]
    global last_update
    last_update = datetime.datetime(temp[0], temp[1], temp[2], temp[3], temp[4], temp[5])
    last_update += datetime.timedelta(hours=4)


def update_last_update_time(new_update_time):
    date_file = open('lastupdate.txt', 'r+')
    date_file.seek(0)
    date_file.write(str(new_update_time))
    date_file.truncate()
    date_file.close()


def read_api_keys():
    global keys
    keys = json.loads(open('keys.json').read())


def init_tweepy():
    if keys is None:
        read_api_keys()

    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    global twitter
    twitter = tweepy.API(auth)


def get_new_tweets(bot_name):
    new_tweets = twitter.search(q='@'+bot_name, rpp=100, show_user=1, include_entities=1)
    new_tweets[:] = [x for x in new_tweets if x.created_at > last_update and x.user.screen_name != bot_name]
    return new_tweets


def reply_to_tweet(text, tweet):
    twitter.update_status(text, in_reply_to_status_id=tweet.id)


def analyze_language_entities(text):
    body = {
        'document': {
            'type': 'PLAIN_TEXT',
            'content': text,
        },
        'encoding_type': 'UTF32',
    }

    service = googleapiclient.discovery.build('language', 'v1')

    request = service.documents().analyzeEntities(body=body)
    return request.execute()


def text_contains(text_obj, search_type):
    # Takes in results of a Google language analysis and checks if
    # any of the entities are of the specified type
    for entity in text_obj:
        if entity['type'] == search_type:
            return True
    return False


def find_nearby_atms(coords, radius=100):
    url = 'http://api.reimaginebanking.com/atms'
    body = {
        'lng': coords[0],
        'lat': coords[1],
        'rad': radius,
        'key': keys['nessie_key']
    }
    response = requests.get(url, body).json()['data']
    print(response.__len__())
    return response


def degrees_to_radians(degrees):
    return degrees * 3.1415 / 180


def find_nearby_banks(coords, radius=1):
    url = 'http://api.reimaginebanking.com/branches'
    body = {
        'key': keys['nessie_key']
    }
    response = requests.get(url, body).json()
    response2 = []
    for bank in response:
        lng = degrees_to_radians(coords[0])
        lat = degrees_to_radians(coords[1])
        lng_diff = degrees_to_radians(coords[0] - bank['geocode']['lng'])
        lat_diff = degrees_to_radians(coords[1] - bank['geocode']['lat'])
        a = math.pow(math.sin(lat_diff/2), 2) + math.pow(math.sin(lng_diff/2), 2) * math.cos(lat) * math.cos(lng)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        earth_radius_miles = 3959
        distance = earth_radius_miles * c
        if distance <= radius:
            bank.distance = distance
            response2.append(bank)
    print(response2.__len__())
    if response2 == []:
        return None
    else:
        # bubblesort time
        swapped = False
        while not swapped:
            swapped = False
            for i in range(1, response2.__len__()):
                if response2[i-1].distance > response2[i].distance:
                    temp = response2[i-1]
                    response2[i-1] = response2[i]
                    response2[i] = temp
                    swapped = True
        return response2


# def get_static_map_atms(center_coords, marker_objs):
#     marker_string = ''
#     for marker in marker_objs:
#         marker_string += str(marker['geocode']['lat']) + ',' + str(marker['geocode']['lng']) + '|'
#     marker_string = marker_string[:-1]
#     url = 'https://maps.googleapis.com/maps/api/staticmap'
#     body = {
#         'center': str(center_coords[0]) + ',' + str(center_coords[1]),
#         'size': '600x400',
#         'markers': marker_string,
#
#     }
#     return requests.get(url, body).json()


# def construct_bank_marker_string(banks):
#     url = 'http://maps.googleapis.com/maps/api/geocode/json'
#     for bank in banks:
#         body = {
#             'address': bank,
#             'key': keys['google_key']
#         }
#         requests.get(url, body).json()

