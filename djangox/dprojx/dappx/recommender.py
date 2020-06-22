import pandas as pd 
import numpy as np 
import random
import math
from math import radians, cos, sin, asin, sqrt

# display trick to display all columns of large dataframes
# from IPython.display import display
# pd.set_option('display.max_columns', None)
# pd.options.mode.chained_assignment = None

# loading network data
def get_network_df(csv_path):
    network_df = pd.read_csv('yelp_dataset/yelp_network_data.csv')
    return network_df

def get_network_df_list(network_df):
    network_df_list = network_df
    network_df_list['friends'] = network_df_list.friends.apply(lambda x: x.split(','))
    return network_df_list

# recommender

# distance function
AVG_EARTH_RADIUS = 6371  # in km
def haversine(point1, point2):
    '''
    Calculate the great-circle distance bewteen two points on the Earth surface
    point1, point2: two tuples, containing the latitude and longitude of each point (decimal degrees)
    Returns the distance bewteen point1 and point2 (kilometers)
    '''
    # unpack latitude/longitude
    lat1, lng1 = point1
    lat2, lng2 = point2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * asin(sqrt(d))
    return h  # in kilometers

def recommend(network_df, network_df_list, user_id, category, k):
    user_reviews_df = network_df_list.loc[network_df['user_id'] == user_id]
    user_pos = (user_reviews_df.iloc[0]['latitude'], user_reviews_df.iloc[0]['longitude'])
    user_friends = user_reviews_df.iloc[0]['friends']
    user_friends.append(user_id) # adding user's own past reviews

    appended_data_list = []
    for friend in user_friends:
        #print(friend)
        friend_reviews_df = network_df_list.loc[network_df_list['user_id'] == friend]
        #print(friend_reviews_df)
        appended_data_list.append(friend_reviews_df)
    appended_data = pd.concat(appended_data_list) # all of users' friends review info
    
    # filtering by category and location
    appended_data = appended_data[appended_data['categories'].str.contains(category, case=False, na=False)]
    appended_data['distance'] = appended_data.apply(lambda x:haversine(user_pos, (x['latitude'], x['longitude'])), axis=1)
    unsorted_data = appended_data[appended_data['distance'] <= 50]
    sorted_data = unsorted_data.sort_values(by=['stars'], ascending=False).drop_duplicates('review_id')
    recommended = sorted_data[['name', 'address', 'city', 'state', 'postal_code', 'stars', 'review_count']].head(k)
    return recommended.groupby(['name', 'address', 'city', 'state', 'postal_code']).mean().sort_values(by=['stars'], ascending=False).reset_index()

# example run
# user_id = 'L498DJb5YDAtoqgv9thWCg'
# category = 'Home Services'
# k = 10
# output = recommend(user_id, category, k)
# print(output.shape)
# print(output)