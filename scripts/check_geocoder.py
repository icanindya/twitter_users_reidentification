# import reverse_geocoder as rg
# import helper
# import statistics as stat
# mongo_client = helper.get_mongo_client()
#
# twitter_db = mongo_client['twitter']
# tweets_col = twitter_db['tweets']
# voters_col = twitter_db['voters']
# ground_truths_col = twitter_db['ground_truths']
#
# tuples = [(x['twitter_id'], x['voter_serial']) for x in ground_truths_col.find({})]
#
# coord_list = set()
# place_types = set()
#
# num_users_with_geo = 0
#
# for i, (twitter_id, voter_serial) in enumerate(tuples):
#
#     voter = voters_col.find_one({'serial': voter_serial})
#     voter['twitter_id'] = twitter_id
#
#     tweet_objs = tweets_col.find({'user.id_str': twitter_id,
#                                   'retweeted_status': {'$exists': False},
#                                   'place.place_type': {'$in': ['poi', 'neighborhood', 'city']}
#                                   })
#
#     tweet_obj_list = list(tweet_objs)
#
#     for tweet_obj in tweet_obj_list:
#         if tweet_obj['place']['place_type'] in ['neighborhood']:
#             lons = []
#             lats = []
#             print(tweet_obj['place']['full_name'], tweet_obj['place']['country'])
#             coordinates = tweet_obj['place']['bounding_box']['coordinates'][0]
#             for coordinate in coordinates:
#                 lons.append(coordinate[0])
#                 lats.append(coordinate[1])
#
#             lon, lat = stat.mean(lons), stat.mean(lats)
#             coord_list.add((lat, lon, tweet_obj['place']['full_name']))
#
#     if len(coord_list) >= 20:
#         break
# coord_list = list(coord_list)
#
# results = rg.search((coord_list[0][0], coord_list[0][1]))
#
# print([c for c in coord_list])
#
# print(results)
#
#
# print('users with geo tweets: {}'.format(num_users_with_geo/len(tuples)))




import reverse_geocoder as rg
import pprint


def reverseGeocode(coordinates):
    result = rg.search(coordinates)

    # result is a list containing ordered dictionary.
    pprint.pprint(result)


# Driver function
if __name__ == "__main__":
    # Coorinates tuple.Can contain more than one pair.
    coordinates = (29.655509, -81.589169)

    reverseGeocode(coordinates)