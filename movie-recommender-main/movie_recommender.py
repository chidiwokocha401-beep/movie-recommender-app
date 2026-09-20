### MOVIE RECOMMENDER SYSTEM
import argparse
import numpy as np
import pandas as pd
import os
from similarity_scores import pearson_score
from collaborative_filtering import find_similar_users

def build_arg_parser():
    parser = argparse.ArgumentParser(description= 'Find users who are similar to input user')
    parser.add_argument('--user', dest= 'user', required= True, help= 'Input user')
    return parser

def get_recommendations(dataset, input_user):
    if input_user not in dataset.userID.values:
        raise TypeError('Cannot find ' + str(input_user) + ' in the dataset')
    
    overall_scores = {}
    similarity_scores = {}
    
    for user in [x for x in dataset.userID.unique() if x != input_user]:
        similarity_score = pearson_score(dataset, input_user, user)
        
        if similarity_score < 0.8: continue
    
        filtered_list = [x for x in dataset[dataset['userID'] == user].movieID.values
                     if x not in dataset[dataset['userID'] == input_user].movieID.values
                    or dataset.loc[(dataset['userID'] == input_user) & (dataset.movieID == x)]
                         ['rating'].iloc[0] == 0]
    
        for item in filtered_list:
            overall_scores.update({
                item: dataset.loc[(dataset['userID'] == user) & (dataset.movieID == item)]['rating'].iloc[0] *
                        similarity_score})
            similarity_scores.update({item: similarity_score})
        
    if len(overall_scores) == 0:
        return ['No recommendations possible']
    
    movie_scores = np.array([[score/similarity_scores[item], item]
                            for item, score in overall_scores.items()])
    
    movie_scores = movie_scores[np.argsort(movie_scores[:, 0])[::-1]]
    movie_recommendations = [movie for _, movie in movie_scores]
    
    return movie_recommendations

if __name__ == '__main__':
    args = build_arg_parser().parse_args()
    user = int(args.user)

    ratings = pd.read_csv(os.path.abspath("movie-recommender-app\\u.data"),
                     sep= '\t',
        names= ['userID', 'movieID', 'rating', 'timestamp'])

    # Loading movie info
    movies = pd.read_csv(os.path.abspath("movie-recommender-app\\u.item"),
                        sep= '|',
                        encoding= 'latin-1',
                        usecols= [0,1],
                        names= ['movieID', 'title'])
    # Merging
    data = pd.merge(ratings, movies, on= 'movieID')
    
    print('\nMovie recommendations for ' + str(user) + ':')
    movies = get_recommendations(data, user)
    for i, movie in enumerate(movies):
        movie_ = data.loc[data['movieID'] == movie]['title'].iloc[0]
        print(str(i+1) + '. ' + movie_)
