from datetime import datetime
import api_calls
import tweepy

# Constants
BOT_NAME = 'bobbys_ramhack'

# Initialize Twitter API
api_calls.init_tweepy()

# Read in the last update time from file
api_calls.read_last_update_time()

# Save new "last updated" time to save to file at end
new_update_time = datetime.now()

tweets = api_calls.get_new_tweets(BOT_NAME)

if tweets.__len__() == 0:
    exit(0)

for tweet in tweets:
    print(tweet.text)
    entities = api_calls.analyze_language_entities(tweet.text)['entities']
    reply_text = '@' + tweet.user.screen_name + ' '
    sentiment = api_calls.analyze_language_sentiment(tweet.text)['documentSentiment']
    if sentiment['score'] < 0:
        reply_text += 'What\'s the magic word?'
    elif api_calls.text_contains(entities, 'LOCATION') is not False:  # Find out if a location was mentioned in the tweet
        if tweet.place is None:
            tweet.place = type('test', (), {})()
            tweet.place.bounding_box = type('test', (), {})()
            tweet.place.bounding_box.coordinates = [[[]]]
            tweet.place.bounding_box.coordinates[0][0] = api_calls.get_coords_from_location(api_calls.text_contains(entities, 'LOCATION')['name'])
        for entity in entities:
            if entity['name'].lower().find('bank') != -1 or entity['name'].lower().find('branch') != -1:
                banks = api_calls.find_nearby_banks(tweet.place.bounding_box.coordinates[0][0])
                if banks is None or banks.__len__() == 0:
                    reply_text += 'Unfortunately there are no banks within range of this location'
                    break
                else:
                    # api_calls.get_static_map_atms(tweet.place.bounding_box.coordinates[0][0], banks)
                    for bank in banks:
                        temp_reply_text = reply_text
                        address = bank['address']
                        temp_reply_text += address['street_number'] +' '+ address['street_name'] +' '+ address['city'] +', '+ address['state'] +', '+ address['zip'] + '\n'
                        if temp_reply_text.__len__() < 140:
                            reply_text = temp_reply_text
                    break
            elif entity['name'].lower().find('atm') != -1:
                atms = api_calls.find_nearby_atms(tweet.place.bounding_box.coordinates[0][0])
                if atms is None or atms.__len__() == 0:
                    reply_text += 'Unfortunately there are no ATMs within range of this location'
                    break
                else:
                    # api_calls.get_static_map_atms(tweet.place.bounding_box.coordinates[0][0], atms)
                    for atm in atms:
                        temp_reply_text = reply_text
                        address = atm['address']
                        temp_reply_text += address['street_number'] +' '+ address['street_name'] +' '+ address['city'] +', '+ address['state'] +', '+ address['zip'] + '\n'
                        if temp_reply_text.__len__() < 140:
                            reply_text = temp_reply_text
                    break
    else:
        for entity in entities:
            if entity['name'].lower().find('bank') != -1 or entity['name'].lower().find('branch') != -1:
                if tweet.place is None:
                    reply_text += 'It looks like you\'re trying to find a nearby bank branch, but your tweet did not have your location attached'
                    break
                banks = api_calls.find_nearby_banks(tweet.place.bounding_box.coordinates[0][0])
                if banks is None or banks.__len__() == 0:
                    reply_text += 'Unfortunately there are no banks within range of this location'
                    break
                else:
                    # api_calls.get_static_map_atms(tweet.place.bounding_box.coordinates[0][0], banks)
                    for bank in banks:
                        temp_reply_text = reply_text
                        address = bank['address']
                        temp_reply_text += address['street_number'] +' '+ address['street_name'] +' '+ address['city'] +', '+ address['state'] +', '+ address['zip'] + '\n'
                        if temp_reply_text.__len__() < 140:
                            reply_text = temp_reply_text
                    break
            elif entity['name'].lower().find('atm') != -1:
                if tweet.place is None:
                    reply_text += 'It looks like you\'re trying to find a nearby ATM, but your tweet did not have your location attached'
                    break
                atms = api_calls.find_nearby_atms(tweet.place.bounding_box.coordinates[0][0])
                if atms is None or atms.__len__() == 0:
                    reply_text += 'Unfortunately there are no ATMs within range of this location'
                    break
                else:
                    # api_calls.get_static_map_atms(tweet.place.bounding_box.coordinates[0][0], atms)
                    for atm in atms:
                        temp_reply_text = str(reply_text)
                        address = atm['address']
                        temp_reply_text += address['street_number'] +' '+ address['street_name'] +' '+ address['city'] +', '+ address['state'] +', '+ address['zip'] + '\n'
                        if temp_reply_text.__len__() < 140:
                            reply_text = temp_reply_text
                    break
    print(reply_text)
    api_calls.reply_to_tweet(reply_text, tweet)

api_calls.update_last_update_time(new_update_time)
