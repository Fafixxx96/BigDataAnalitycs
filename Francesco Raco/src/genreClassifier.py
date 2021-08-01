import logging

import matplotlib

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
def log_speechiness(row):
    res = list(row)
    l = float(numpy.log(res[9]))
    res[9] = l
    return res
"""

"""
The following is the function that will be utilized, once the clustering is done, to map each track with the proper genre.
"""

def map_features(track):
    label = 0
    distance = 100000000
    centroids_for_mapping = centroids[chosen_K_value]
    track_np = numpy.array(list(track), dtype='float64')
    for i in range(0, len(centroids_for_mapping)):
        current_centroid = numpy.array(centroids_for_mapping[i])
        new_distance = numpy.linalg.norm(track_np - current_centroid)
        if new_distance < distance:
            label = i
            distance = new_distance
    result = list(track)
    result.append(label)
    return result

def map_features_buckets(track):
    label = 0
    distance = 100000000
    centroids_for_mapping = centroids[chosen_K_value]
    track_np = numpy.array(list(track)) #dtype='float64'
    #print(track_np)
    #print(track_np.dtype)
    #print(numpy.array(centroids[0]).dtype)
    for i in range(0, len(centroids_for_mapping)):
        current_centroid = numpy.array(centroids_for_mapping[i])
        #print("current centroid : " + str(current_centroid))
        new_distance = numpy.linalg.norm(track_np - current_centroid)
        #print("current new distance: "+ str(new_distance))
        if new_distance < distance:
            label = i
            distance = new_distance
    result = []
    for elem in track_np[0]:
        result.append(float(elem))
    result.append(float(label))
    return list(result)


"""
Define the credentials
"""

client_id = "4b7a6ff9e9e242208bcb12834b0244ac"
client_secret = "786b8540a1c74b3491db3f8f1170185d"
redirect_uri = "http://localhost:8080"
scope = "playlist-read-private"

"""
Creation of the Spotify Client
"""

client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope))

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
    drop('genres')
#.drop('mode').drop('speechiness')

starting_genres_df.show(10)


#print("computing log speechiness rdd")
"""
genres_rdd = spark.createDataFrame(starting_genres_df.collect()).rdd
#genres_rdd = starting_genres_df.rdd
log_genres = genres_rdd.map(lambda x: log_speechiness(x))


genres_tmp = spark.createDataFrame(log_genres,schema=starting_genres_df.columns)
genres_tmp.show(10)
"""
print("computing log_df")
log_df = starting_genres_df.withColumn("log_speechiness", functions.log("speechiness"))
log_df.show(10)

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

#print("total number of tracks: " + str(starting_tracks_df.count()))
#print("tracks without null values: " + str(starting_tracks_df.dropna().count()))

#print("total number of rows: " + str(starting_genres_df.count()))
#print("number of rows without null values: " + str(starting_genres_df.replace("[]", None).dropna().count()))

#starting_genres_df.show()


"""
Now we group together the features into vectors of doubles, and then we scale them to have values between 0 and 1.
"""

features_columns = starting_genres_df.columns
#features_columns = log_df.drop('speechiness').columns
assembler = VectorAssembler().setInputCols(features_columns).setOutputCol('features')
assembled_df = assembler.transform(starting_genres_df).select('features')

min_max_scaler = MinMaxScaler().setMin(0).setMax(1).setInputCol('features').setOutputCol('scaled_features')
fitted_scaler = min_max_scaler.fit(assembled_df)
scaled_genres_df = fitted_scaler.transform(assembled_df).select('scaled_features')

#for row in scaled_genres_df.collect()[0:10]:
   # print(row)
#for row in scaled_genres_df.collect():
 #   print(row)
#print(features_columns)

"""
Let's first try DBSCAN for clustering. Different values of eps and min_samples will be tested 
in order to find the best configuration.
"""

eps_range = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.60, 0.65, 0.70]
samples_range = range(3,11)

for eps in eps_range:
    for n in samples_range:
        X_db = []
        for elem in scaled_genres_df.collect():
            X_db.append(list(elem['scaled_features']))
        dbscan = DBSCAN(eps=eps,min_samples=n).fit(X_db)

        db_score = silhouette_score(X_db,dbscan.labels_)
        print("Silhouette score for DBSCAN with eps=" + str(eps) + " and min_samples=" + str(n) + " is = " + str(db_score))
        print("Clusters: " + str(numpy.unique(dbscan.labels_)))
        print("\n")



"""
DBSCAN doesn't provide good results. Let's try now the K-Means clustering. We'll test different K values,
starting with 5, since for the purpose of the project smaller values would be useless.
"""

k_start = 5
k_range = list(range(k_start,16))
silhouette_km = []
centroids = {}


for k in k_range:
    print('results for k = ' + str(k))

    model = KMeans().setK(k).setMaxIter(50).setDistanceMeasure('euclidean').setFeaturesCol('scaled_features')
    fitted_km = model.fit(scaled_genres_df)
    summary = fitted_km.summary
    inertia = summary.trainingCost
    print("inertia = " + str(inertia))

    transformed_df = fitted_km.transform(scaled_genres_df)

    X = []
    for elem in transformed_df.select('scaled_features').collect():
        X.append(list(elem['scaled_features']))

    #for elem in transformed_df.select('scaled_features').collect():
     #   X.append(list(elem))
    labels = []
    for elem in transformed_df.select('prediction').collect():
        labels.append(elem['prediction'])
    #print(tmp)
    #labels = numpy.array(labels)
    #print(X)
    #for array in X:
     #   print(array)

    #for elem in transformed_df.select('scaled_features').collect():   -->   kmeans_sk.labels_
     #   print(elem)
    #transformed_df.show()

    evaluator = ClusteringEvaluator()
    silhouette = evaluator.setFeaturesCol('scaled_features').setPredictionCol('prediction').evaluate(transformed_df)
    silhouette_km.append(silhouette)
    print("for k = " + str(k) + ", the silhouette score (pyspark) is: " + str(silhouette))

    kmeans_sk = km(n_clusters=k, random_state=1899).fit(X)
    silhouette_sk = silhouette_score(X=X, labels=kmeans_sk.labels_, metric='sqeuclidean')
    print("for k = " + str(k) + ", the silhouette score (sklearn) is: " + str(silhouette_sk) + "\n")
    silhouette_km.append(silhouette_sk)
    #print(kmeans_sk.cluster_centers_)
    centroids[k] = kmeans_sk.cluster_centers_

    plt.figure(figsize=(9,9))
    predictions = kmeans_sk.labels_
    samples = silhouette_samples(X=X, labels= predictions)

    padding = len(X)
    pos = padding
    ticks = []

    for i in range(k):
        coeffs = samples[predictions == i]
        coeffs.sort()

        color = matplotlib.cm.Spectral(i / k)
        plt.fill_betweenx(numpy.arange(pos, pos + len(coeffs)), 0, coeffs,
                          facecolor=color, edgecolor=color, alpha=0.7)
        ticks.append(pos + len(coeffs) // 2)
        pos += len(coeffs) + padding

    plt.gca().yaxis.set_major_locator(FixedLocator(ticks))
    plt.gca().yaxis.set_major_formatter(FixedFormatter(range(k)))
    plt.gca().set_xticks([-0.1, 0, 0.2, 0.4, 0.6])
    plt.axvline(x=silhouette_sk, color="red", linestyle="--")
    plt.title("$k={}$".format(k), fontsize=16)
    plt.show()

    #centroids = fitted_km.clusterCenters()
    #print("number of centroids is: " + str(len(centroids)))
    #for centroid in centroids:
        #print(centroid)

chosen_K_value = 7
"""
As we see, the best result is with KMeans with K=7. Let's now implement the classifier, by trying both Naive Bayes 
and Decision Tree. 
"""


tracks_tmp_df = starting_tracks_df.select(features_columns)
tracks_assembler = VectorAssembler().setInputCols(features_columns).setOutputCol('features')
assembled_tracks_df = tracks_assembler.transform(tracks_tmp_df).select('features')


tracks_scaler = MinMaxScaler().setMin(0).setMax(1).setInputCol('features').setOutputCol('scaled_tracks_features')
fitted_tracks_scaler = tracks_scaler.fit(assembled_tracks_df)
scaled_tracks_df = fitted_tracks_scaler.transform(assembled_tracks_df).select('scaled_tracks_features')

#mappedDF = map_features(Column('scaled_tracks_features'))

tracks_rdd = scaled_tracks_df.rdd
mapped_rdd = tracks_rdd.map(lambda x: map_features(x))
"""
cols_buckets = tracks_tmp_df.columns
cols_buckets_with_label = tracks_tmp_df.columns
cols_buckets_with_label.append('label')
"""
mapped_df = spark.createDataFrame(mapped_rdd.collect(), schema=['features', 'label']) #features [tracks_tmp_df.columns, 'label'] cols_buckets_with_label
mapped_df.show()
print(numpy.unique(mapped_df.select('label').collect()))
"""
borders = [numpy.NINF, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, numpy.PINF]
cols_array = []
for i in range(0,len(cols_buckets)):
    cols_array.append(borders)
output_cols = []
for j in cols_buckets:
    output_cols.append("bucketized_"+str(j))

bucketizer = Bucketizer(splitsArray=cols_array, inputCols=cols_buckets, outputCols=output_cols)



#mapped_df.show()
bucketized_df = bucketizer.transform(mapped_df)
bucketized_df.show()

#for elem in mapped_df.collect():
    #print(elem)

buckets_assembler = VectorAssembler().setInputCols(output_cols).setOutputCol('features')
assembled_bucketized_df = buckets_assembler.transform(bucketized_df).select('features','label')
"""
training_set, test_set = mapped_df.randomSplit([0.8,0.2])
nb = NaiveBayes().setFeaturesCol('features').setLabelCol('label')
nb_evaluator = MulticlassClassificationEvaluator().setLabelCol('label').setPredictionCol('prediction')
nb_params = ParamGridBuilder().addGrid(nb.smoothing, [1.0, 0.1, 0.01, 0.001, 0.0001]).build()
nb_validator = CrossValidator().setEstimator(nb).setEvaluator(nb_evaluator).setEstimatorParamMaps(nb_params).setNumFolds(10)

fitted_nb = nb_validator.fit(training_set)

nb_prediction = fitted_nb.transform(test_set)

nb_accuracy = nb_evaluator.evaluate(nb_prediction)

print("accuracy of NB classifier for k = " + str(chosen_K_value) + " is  " + str(nb_accuracy))

dt = DecisionTreeClassifier().setFeaturesCol('features').setLabelCol('label')
dt_evaluator = MulticlassClassificationEvaluator().setLabelCol('label').setPredictionCol('prediction')
dt_params = ParamGridBuilder().\
    addGrid(dt.impurity, ['gini', 'entropy']).\
    addGrid(dt.maxDepth,[5, 8, 10]).build()
dt_validator = CrossValidator().setEstimator(dt).setEvaluator(dt_evaluator).setEstimatorParamMaps(dt_params).setNumFolds(10)

#addGrid(dt.maxBins, [8, 10, 12])

fitted_dt = dt_validator.fit(training_set)
dt_prediction = fitted_dt.transform(test_set)
dt_accuracy = dt_evaluator.evaluate(dt_prediction)

print("accuracy of DT classifier for k = " + str(chosen_K_value) + " is  " + str(dt_accuracy))












"""
tracks_schema = StructType([
    StructField("id", StringType(), True),
    StructField("name", StringType(), True),
    StructField("popularity", IntegerType(), True),
    StructField("duration_ms", IntegerType(), True),
    StructField("explicit", DoubleType(), True),
    StructField("artists", StringType(), True),
    StructField("id_artists", StringType(), True),
    StructField("release_date", StringType(), True),
    StructField("danceability", DoubleType(), True),
    StructField("energy", DoubleType(), True),
    StructField("key", IntegerType(), True),
    StructField("loudness", DoubleType(), True),
    StructField("mode", IntegerType(), True),
    StructField("speechiness", DoubleType(), True),
    StructField("acousticness", DoubleType(), True),
    StructField("instrumentalness", DoubleType(), True),
    StructField("liveness", DoubleType(), True),
    StructField("valence", DoubleType(), True),
    StructField("tempo", DoubleType(), True),
    StructField("time_signature", IntegerType(), True)
])

starting_tracks_df = spark.\
    read.\
    format("csv").\
    option("header", "true").\
    schema(tracks_schema).\
    load(tracks_path).\
    cache()


The following is a list of Row objects containing the IDs of the tracks


tracks_ids = starting_tracks_df.select("id").collect()

ids = []

for row in tracks_ids:
    ids.append(row['id'])

slice = ids[503000:504000]

albums = []

for id in slice:
    track = client.track(track_id=id)
    album_id = track['album']['id']
    albums.append(client.album(album_id=album_id)['genres'])


for item in albums:
    print(item)

"""


























































