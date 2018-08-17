from time import strftime, localtime
import pandas as pd
import warnings

from .elasticsearch import *

## TODO: use pd.merge to merge followers and Following
##       use pd.concat to concat two different users
##       merge_df = pd.merge(followers, following, on= object.username, how="inner")

Tweets_df = None
Follow_df = None
User_df = None

_object_blocks = {
    "tweet": [],
    "user": [],
    "follow": []
}
_type = ""

def _concat(df):
    if df is None:
        df = pd.DataFrame(_object_blocks["follow"])
    else:
        _df = pd.DataFrame(_object_blocks["follow"])
        df = pd.concat([df, _df], sort=True)
    return df

def _autoget(type):
    global Tweets_df
    global Follow_df
    global User_df

    if type == "search":
        Tweets_df = _concat(Tweets_df)
    if type == "follow":
        Follow_df = _concat(Follow_df)
    if type == "profile":
       User_df = _concat(User_df)

def update(object, config):
    global _type

    try:
        _type = ((object.type == "tweet")*"tweet" +
                 (object.type == "user")*"user")
    except AttributeError:
        _type = "follow"

    if _type == "tweet":
        dt = f"{object.datestamp} {object.timestamp}"
        _data = {
            "id": object.id,
            "date": dt,
            "timezone": object.timezone,
            "location": object.location,
            "tweet": object.tweet,
            "hashtags": object.hashtags,
            "user_id": object.user_id,
            "username": object.username,
            "link": object.link,
            "retweet": object.retweet,
            "user_rt": object.user_rt,
            "essid": str(config.Essid),
            'mentions': object.mentions
            }
        _object_blocks[_type].append(_data)
    elif _type == "user":
        _data = {
            "id": object.id,
            "name": object.name,
            "username": object.username,
            "bio": object.bio,
            "location": object.location,
            "url": object.url,
            "join_datetime": object.join_date + " " + object.join_time,
            "join_date": object.join_date,
            "join_time": object.join_time,
            "tweets": object.tweets,
            "following": object.following,
            "followers": object.followers,
            "likes": object.likes,
            "media": object.media_count,
            "private": object.is_private,
            "verified": object.is_verified,
            "avatar": object.avatar,
            "session": str(config.Essid)
            }
        _object_blocks[_type].append(_data)
    elif _type == "follow":
        _data = {
            config.Following*"following" + config.Followers*"folloers" :
                             {config.Username: object[config.Username]}
        }
        _object_blocks[_type] = _data
    else:
        print("Wrong type of object passed!")

def clean():
    _object_blocks["tweet"].clear()
    _object_blocks["follow"].clear()
    _object_blocks["user"].clear()


def save(_filename, _dataframe, **options):
    if options.get("dataname"):
        _dataname = options.get("dataname")
    else:
        _dataname = "twint"

    if not options.get("type"):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _store = pd.HDFStore(_filename + ".h5")
            _store[_dataname] = _dataframe
            _store.close()
    elif options.get("type") == "Pickle":
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _dataframe.to_pickle(_filename + ".pkl")
    else:
        print("""Please specify: filename, DataFrame, DataFrame name and type
              (HDF5, default, or Pickle)""")

def read(_filename, **options):
    if not options.get("dataname"):
        _dataname = "twint"
    else:
        _dataname = options.get("dataname")

    if not options.get("type"):
        _store = pd.HDFStore(_filename + ".h5")
        _df = _store[_dataname]
        return _df
    elif options.get("type") == "Pickle":
        _df = pd.read_pickle(_filename + ".pkl")
        return _df
    else:
        print("""Please specify: DataFrame, DataFrame name (twint as default),
              filename and type (HDF5, default, or Pickle""")
