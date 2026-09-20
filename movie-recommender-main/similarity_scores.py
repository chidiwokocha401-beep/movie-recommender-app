### SIMILARITY SCORES FOR MOVIELENS DATASET
import pandas as pd
import argparse
import json
import numpy as np
import os


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description= 'Compute Similarity Score')
    parser.add_argument('--user1', dest= 'user1',
                        required= True, help= 'First User')
    parser.add_argument('--user2', dest= 'user2',
                        required= True, help= 'Second User')
    parser.add_argument('--score-type', dest= 'score_type',
                        required= True,
                        choices= ['Euclidean', 'Pearson'],
                        help= 'similarity metric to use')
    return parser

# compute the Euclidean distance score between user1 and user2 
def euclidean_score(data, user1, user2):
    if user1 not in data.userID.values:
            raise TypeError('Cannot find ' +  str(user1) + 'in the data ')

    if  user2 not in data.userID.values:        
            raise TypeError('Cannot find ' +  str(user2) + 'in the data ')
       
     # Movies rated by both user1 and user2 
    
    for item in data[data['userID'] == user1]['movieID'].values:
        if item in data[data['userID'] == user2]['movieID'].values:
            break
    else:
        # if there are no common movies between the users, 
        return 0

    squared_diff = []
    
    for item in data[data['userID'] == user1]['movieID'].values:
        if item in data[data['userID'] == user2]['movieID'].values:
            squared_diff.append(np.square(data.loc[(data['userID'] == user1) & (data.movieID == item)]['rating'].iloc[0] -
                                          data.loc[(data['userID'] == user2) & (data.movieID == item)]['rating'].iloc[0]))
        
    return 1 / (1 + np.sqrt(np.sum(squared_diff)))

# compute the pearson correlation score between user1 and user2 
def pearson_score(data, user1, user2):
    if user1 not in data.userID.values:
        raise TypeError('Cannot find '+ str(user1) + 'in the data')
    if user2 not in data.userID.values:
            raise TypeError('cannot find' + str(user2) + 'in the data')

    # Movie rated by both user1 and user2
    common_movies = {}

    for item in data[data['userID'] == user1]['movieID'].values:
        if item in data[data['userID'] == user2]['movieID'].values:
            common_movies[item] = 1

    num_ratings = len(common_movies)

    # If there are no common movies between user1 and user2, then the score is 0
    if num_ratings == 0:
        return 0

    # calculate the sum of ratings of all the common movies
    user1_sum = np.sum([data.loc[(data['userID'] == user1) & (data.movieID == item)]['rating'].iloc[0]
                        for item in common_movies])
    user2_sum = np.sum([data.loc[(data['userID'] == user2) & (data.movieID == item)]['rating'].iloc[0]
                        for item in common_movies])

    # calculate the sum of squares of ratings of all the common movies 
    user1_squared_sum = np.sum([np.square(data.loc[(data['userID'] == user1) & (data.movieID == item)]
                                          ['rating'].iloc[0]) for item in common_movies])
    user2_squared_sum = np.sum([np.square(data.loc[(data['userID'] == user2) & (data.movieID == item)]
                                          ['rating'].iloc[0]) for item in common_movies])

    # calculate the sum of products of the ratings of the common movies
    sum_of_products = np.sum([data.loc[(data['userID'] == user1) & (data.movieID == item)]['rating'].iloc[0]
                              * 
                              data.loc[(data['userID'] == user2) & (data.movieID == item)]['rating'].iloc[0]
                              for item in common_movies])

    # calculate the pearson correlation score
    Sxy = sum_of_products - (user1_sum * user2_sum / num_ratings)
    Sxx = user1_squared_sum - np.square(user1_sum) / num_ratings
    Syy = user2_squared_sum - np.square(user2_sum) / num_ratings

    if Sxx * Syy == 0:
        return 0

    return Sxy / np.sqrt(Sxx * Syy)

if __name__ =='__main__':
    args = build_arg_parser().parse_args()
    user1 = int(args.user1)
    user2 = int(args.user2)
    score_type = args.score_type
    
    ratings = pd.read_csv(os.path.abspath("movie-recommender-main\\u.data"),
                     sep= '\t',
        names= ['userID', 'movieID', 'rating', 'timestamp'])

    # Loading movie info
    movies = pd.read_csv(os.path.abspath("movie-recommender-main\\u.item"),
                        sep= '|',
                        encoding= 'latin-1',
                        usecols= [0,1],
                        names= ['movieID', 'title'])
    # Merging
    data = pd.merge(ratings, movies, on= 'movieID')
        
    # Old version using json-----------------
    # rating_files = 'rating.json'
    
    #with open(ratings_file, 'r') as f:
    #    data = json.loads (f.read())
     
    if score_type == 'Euclidean':
        print("\nEuclidean score:")
        print(euclidean_score(data, user1, user2))
    else:
        print("\nPearson score:")
        print(pearson_score(data, user1, user2))
