import requests
import pytz
import datetime

import misc

# input must be an array of videos
def print_videos_from_resources(videos):
    for i in range(0, len(videos)):
        snippet = videos[i]['snippet']
        print("VIDEO ID :", videos[i]['id']['videoId'])

        for j in snippet:
            print('\t', j, ':\t', snippet[j])

        misc.print_separator()

def print_videos_from_videos(videos):
    for i in range(0, len(videos)):
        snippet = videos[i]['snippet']
        stats = videos[i]['statistics']
        print("VIDEO ID :", videos[i]['id'])

        print("snippet:")
        for j in snippet:
            if j!='description' and j!='thumbnails' and j!='localized':
                print('\t', j, ':\t', snippet[j])

        print("statistics:")
        for j in stats:
            print('\t', j, ':\t', stats[j])

        misc.print_separator()

def build_request(api_url : str, request : str, parameters : dict, noexcept : bool = False) -> str:
    if (len(parameters) == 0 or "key" not in parameters) and noexcept == False:
        misc.throw_exception("invalid build request")

    request_url = api_url + '/' + request + '?'

    flag = False

    for i in parameters:
        if (flag == True):
            request_url += '&'
        request_url += (i + '=' + parameters[i])
        flag = True

    return request_url

def test_api_response():
    params = {
    'key' : misc.api_key,
    'part' : 'snippet',
    'q' : 'ragnarok'
    }

    request = build_request(misc.api_url, 'search', params)
    print('request:', request)
    misc.print_separator()

    response = requests.get(url=request)
    data = response.json()
    items = data['items']

    print_videos_from_resources(items)

#returns videos resource
def request_chart(country_code : str = "RU", max_results : int = 5):
    if len(country_code) != 2:
        misc.throw_exception('invalid chart request')

    if max_results > 50:
        max_results = 50

    params = {
        'key' : misc.api_key,
        'part' : 'snippet,statistics',
        'chart' : 'mostPopular',
        'maxResults' : str(max_results),
        'regionCode' : country_code
    }

    request = build_request(misc.api_url, 'videos', params)
    misc.print_separator()
    print('request:', request)
    misc.print_separator()

    response = requests.get(url=request)
    data1 = response.json()
    items1 = data1['items']

    j = 1
    channels=''
    for i in range(0, len(items1)):
        channels += items1[i]['snippet']['channelId']
        if j != len(items1):
            channels += ','
    
    params = {
        'key' : misc.api_key,
        'part' : 'snippet,statistics,contentDetails',
        'id' : channels
    }

    request = build_request(misc.api_url, 'channels', params)
    misc.print_separator()
    print('request:', request)
    misc.print_separator()

    response = requests.get(url=request)
    data2 = response.json()
    items2 = data2['items']


    return [items1, items2]

def extract_data_from_video_resource(video, from_chart : bool = False):

    title = (video['snippet']['title']).replace("'","`")

    data = {
        'video_id' : video['id'], 
        'video_name' : title, 
        'channel_id' : video['snippet']['channelId'],
        'view_count' : video['statistics']['viewCount'],
        'like_count' : '0',
        'dislike_count' : '0',
        'like_ratio' : '0',
        'comment_count' : '0',
        'trended_on' : '0'
    }

    try:
        data['dislike_count'] = video['statistics']['dislikeCount']
    except:
        data['dislike_count'] = 'NULL'

    try:
        data['like_ratio'] = str(round(float(video['statistics']['likeCount']) / float(video['statistics']['dislikeCount']), 2))
    except:
        data['like_ratio'] = 'NULL'

    try:
        data['comment_count'] = video['statistics']['commentCount']
    except:
        data['comment_count'] = 'NULL'

    try:
        data['like_count'] = video['statistics']['likeCount']
    except:
        data['like_count'] = 'NULL'

    if from_chart:
        data['trended_on'] = str(datetime.datetime.now(pytz.utc))
    
    return data

def extract_data_from_channel_resource(channel, region : str = 'NULL'):
    data = {
        'channel_id' : channel['id'],
        'subscriber_count' : str(channel['statistics']['subscriberCount']),
        'subscriber_count_hidden' : str(channel['statistics']['hiddenSubscriberCount']),
        'video_count' : str(channel['statistics']['videoCount']),
        'total_views' : str(channel['statistics']['viewCount']),
        'region' : region
    }
    
    return data