import logging
import matplotlib
from numpy import double

logging.basicConfig(level= logging.ERROR)
import numpy
import math
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import json
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import Column
from pyspark.sql import functions
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, IntegerType, ArrayType, DateType
from pyspark.ml.feature import VectorAssembler, MinMaxScaler
from pyspark.ml.clustering import KMeans, KMeansModel, KMeansSummary
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.classification import NaiveBayes, DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import Bucketizer
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans as km
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter


"""
The following is the function that will be utilized, once the clustering is done, to map each track with the proper genre.
"""

def map_features(track):
    label = 0
    distance = 100000000
    track_np = numpy.array(list(track), dtype='float64')
    for i in range(0, len(centroids)):
        current_centroid = numpy.array(centroids[i])
        new_distance = numpy.linalg.norm(track_np - current_centroid)
        if new_distance < distance:
            label = i
            distance = new_distance
    result = list(track)
    result.append(label)
    return result


"""
A function for saving the audio features of the user's favorite tracks into the same representation of the Kaggle dataset,
in order to use the same preprocessing.
"""
def map_saved_track(track):
    popularity = track['popularity']
    result = []
    audio_features = client.audio_features(track['id'])[0]
    header = list(features_columns)
    header.remove('popularity')
    header.remove('key')
    result.append(track['name'])
    result.append(track['id'])
    for elem in header:
        result.append(float(audio_features[elem]))
    result.append(float(popularity))
    result.append(float(audio_features['key']))
    return result


"""
Creation of the SparkSession and loading of the starting datasets into dataframes
"""

spark = SparkSession.builder.\
    master("local[*]").\
    appName("genreClassifier").\
    config("spark.some.config.option", "some-value").\
    getOrCreate()

spark.sparkContext.setLogLevel('ERROR')

tracks_path = "C:\\Users\\franc\\PycharmProjects\\bdaProject\\data\\tracks.csv"

genres_path = "C:\\Users\\franc\\PycharmProjects\\bdaProject\\data\\genres.csv"

genres_schema = StructType([
    StructField("mode", DoubleType(), True),
    StructField("genres", StringType(), True),
    StructField("acousticness", DoubleType(), True),
    StructField("danceability", DoubleType(), True),
    StructField("duration_ms", DoubleType(), True),
    StructField("energy", DoubleType(), True),
    StructField("instrumentalness", DoubleType(), True),
    StructField("liveness", DoubleType(), True),
    StructField("loudness", DoubleType(), True),
    StructField("speechiness", DoubleType(), True),
    StructField("tempo", DoubleType(), True),
    StructField("valence", DoubleType(), True),
    StructField("popularity", DoubleType(), True),
    StructField("key", DoubleType(), True)
])

starting_genres_df = spark.\
    read.\
    format("csv").\
    option("header", "true").\
    schema(genres_schema).\
    load(genres_path).\
    drop('genres').cache()

tracks_schema = StructType([
    StructField("id", StringType(), True),
    StructField("name", StringType(), True),
    StructField("popularity", DoubleType(), True),
    StructField("duration_ms", DoubleType(), True),
    StructField("explicit", DoubleType(), True),
    StructField("artists", StringType(), True),
    StructField("id_artists", StringType(), True),
    StructField("release_date", StringType(), True),
    StructField("danceability", DoubleType(), True),
    StructField("energy", DoubleType(), True),
    StructField("key", DoubleType(), True),
    StructField("loudness", DoubleType(), True),
    StructField("mode", DoubleType(), True),
    StructField("speechiness", DoubleType(), True),
    StructField("acousticness", DoubleType(), True),
    StructField("instrumentalness", DoubleType(), True),
    StructField("liveness", DoubleType(), True),
    StructField("valence", DoubleType(), True),
    StructField("tempo", DoubleType(), True),
    StructField("time_signature", DoubleType(), True)
])

starting_tracks_df = spark.\
    read.\
    format("csv").\
    option("header", "true").\
    schema(tracks_schema).\
    load(tracks_path).dropna().cache()

"""
Now we group together the genres features into vectors of doubles, and then we scale them to have values between 0 and 1.
"""

features_columns = starting_genres_df.columns
assembler = VectorAssembler().setInputCols(features_columns).setOutputCol('features')
assembled_df = assembler.transform(starting_genres_df).select('features')

min_max_scaler = MinMaxScaler().setMin(0).setMax(1).setInputCol('features').setOutputCol('scaled_features')
fitted_scaler = min_max_scaler.fit(assembled_df)
scaled_genres_df = fitted_scaler.transform(assembled_df).select('scaled_features')

"""
Lets implement KMeans
"""
print("starting clustering")
chosen_K = 7

X = []
for elem in scaled_genres_df.select('scaled_features').collect():
    X.append(list(elem['scaled_features']))

kmeans_sk = km(n_clusters=chosen_K, random_state=1899).fit(X)
centroids = kmeans_sk.cluster_centers_

"""
Let's now implement the classifier.
"""
print("starting classification")
tracks_tmp_df = starting_tracks_df.select(features_columns)
tracks_assembler = VectorAssembler().setInputCols(features_columns).setOutputCol('features')
assembled_tracks_df = tracks_assembler.transform(tracks_tmp_df).select('features')


tracks_scaler = MinMaxScaler().setMin(0).setMax(1).setInputCol('features').setOutputCol('scaled_tracks_features')
fitted_tracks_scaler = tracks_scaler.fit(assembled_tracks_df)
scaled_tracks_df = fitted_tracks_scaler.transform(assembled_tracks_df).select('scaled_tracks_features')

tracks_rdd = scaled_tracks_df.rdd
mapped_rdd = tracks_rdd.map(lambda x: map_features(x))
mapped_df = spark.createDataFrame(mapped_rdd.collect(), schema=['features', 'label'])

training_set, test_set = mapped_df.randomSplit([0.8,0.2])
print("preprocessing done. creating the classifier")

dt = DecisionTreeClassifier().setFeaturesCol('features').setLabelCol('label')
dt_evaluator = MulticlassClassificationEvaluator().setLabelCol('label').setPredictionCol('prediction')
dt_params = ParamGridBuilder().\
    addGrid(dt.impurity, ['gini', 'entropy']).\
    addGrid(dt.maxDepth,[5, 8, 10]).build()
dt_validator = CrossValidator().setEstimator(dt).setEvaluator(dt_evaluator).setEstimatorParamMaps(dt_params).setNumFolds(10)

fitted_dt = dt_validator.fit(training_set)
dt_prediction = fitted_dt.transform(test_set)
dt_accuracy = dt_evaluator.evaluate(dt_prediction)

print("accuracy of DT classifier for k = " + str(chosen_K) + " is  " + str(dt_accuracy))

"""
Define the credentials
"""

client_id = ""
client_secret = ""

redirect_uri = "http://localhost:8085"
scope ="user-library-read"
#"playlist-read-private"

"""
Creation of the Spotify Client
"""

client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope))

tracks_batch = 50
playlist = client.current_user_saved_tracks(limit=tracks_batch)
tracks = playlist['items']
total_tracks = playlist['total']
remaining_tracks = total_tracks - tracks_batch
offset = 50


while remaining_tracks > 0:
    if remaining_tracks >= tracks_batch:
        tmp = client.current_user_saved_tracks(limit=tracks_batch, offset=offset)
        for elem in tmp['items']:
            tracks.append(elem)
        offset = offset + tracks_batch
        remaining_tracks = remaining_tracks - tracks_batch
    else:
        tmp = client.current_user_saved_tracks(limit=remaining_tracks,offset=offset)
        for elem in tmp['items']:
            tracks.append(elem)
        offset = offset+remaining_tracks
        remaining_tracks = 0



print("\n")
saved_tracks = []
for elem in tracks:
    saved_tracks.append(map_saved_track(elem['track']))


for elem in saved_tracks:
    print(elem)

favorite_tracks_header = list(features_columns)
favorite_tracks_header.insert(0,'id')
favorite_tracks_header.insert(0,'name')

favorite_tracks_schema = StructType([
    StructField("name", StringType(), True),
    StructField("id", StringType(), True),
    StructField("mode", DoubleType(), True),
    StructField("acousticness", DoubleType(), True),
    StructField("danceability", DoubleType(), True),
    StructField("duration_ms", DoubleType(), True),
    StructField("energy", DoubleType(), True),
    StructField("instrumentalness", DoubleType(), True),
    StructField("liveness", DoubleType(), True),
    StructField("loudness", DoubleType(), True),
    StructField("speechiness", DoubleType(), True),
    StructField("tempo", DoubleType(), True),
    StructField("valence", DoubleType(), True),
    StructField("popularity", DoubleType(), True),
    StructField("key", DoubleType(), True)
])
favorite_tracks_df = spark.createDataFrame(data=saved_tracks,schema=favorite_tracks_header)
print("favorite tracks dataframe created")
favorite_tracks_assembler = VectorAssembler().setInputCols(features_columns).setOutputCol('features')
favorite_tracks_assembled_df = favorite_tracks_assembler.transform(favorite_tracks_df).select('name','id','features')
favorite_tracks_scaler = MinMaxScaler().setMin(0).setMax(1).setInputCol('features').setOutputCol('scaled_favorite_tracks_features')
fitted_favorite_tracks_scaler = favorite_tracks_scaler.fit(favorite_tracks_assembled_df)
scaled_favorite_tracks_df = fitted_favorite_tracks_scaler.transform(favorite_tracks_assembled_df).select('name','id', 'scaled_favorite_tracks_features').withColumnRenamed("scaled_favorite_tracks_features", "features")
scaled_favorite_tracks_df.show()
only_features_df = scaled_favorite_tracks_df.select('features')
favorite_tracks_predictions = fitted_dt.transform(only_features_df)
final_df = scaled_favorite_tracks_df.join(favorite_tracks_predictions, 'features', 'inner')

print("tracks scaling done")

print("mapping done")

user_id = 'prp468n1n5qp2sdr1ps5hk8t0'
playlists_names = []
scope2 = 'playlist-modify-public'
client2 = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope2))
for i in range(chosen_K):
    current_name = "genre " + str(i)
    current_playlist = client2.user_playlist_create(user=user_id,name = current_name)
    playlists_names.append(current_name)
    print("current playlist's id is: " + str(current_playlist['id']))
    playlist_subset = final_df.where(final_df.prediction == i).select('id').collect()
    id_list = []
    for elem in playlist_subset:
        id_list.append(elem['id'])
    print(id_list)
    if len(id_list) > 0:
        client2.playlist_add_items(playlist_id=current_playlist['id'], items=id_list)



