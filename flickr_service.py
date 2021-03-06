import flask
from flask import request, jsonify
import requests
import json
import os


app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Flickr Reader Service</h1>
            <p>Try '/collections-metadata' or '/download-assets'</p>'''


@app.route('/collections-metadata', methods=['GET'])
def collections_metadata():

    if 'url' in request.args:
        url = request.args['url']
    else:
        return "Error: No Collection URL was provided"


    path_parts = url.split('/')
    user_id = path_parts[4]
    collection_id = path_parts[6]

    # Sample URL:
    # https://www.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key=a729ddbdafe5c5dec056c2217ed488ce&photoset_id=72157638428210105&user_id=11061732%40N07&format=json&nojsoncallback=1

    user_id = user_id.replace("@","%40")

    request_url = ("https://www.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key=a729ddbdafe5c5dec056c2217ed488ce&"
        + "photoset_id=" + collection_id + "&user_id=" + user_id + "&format=json&nojsoncallback=1")
    strlist = requests.get(request_url).content
    results = json.loads(strlist)

    if 'message' in results or 'photoset' not in results or 'photo' not in results['photoset']:
        return jsonify(results)

    photos_response = []

    for photo in results['photoset']['photo']:
        title = photo['title']
        photo_id = photo['id']

        # Sample URL: 
        # https://www.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key=a729ddbdafe5c5dec056c2217ed488ce&photo_id=11242850886&format=rest

        photo_request_url = ("https://www.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key=a729ddbdafe5c5dec056c2217ed488ce&"
        + "photo_id=" + photo_id + "&format=json&nojsoncallback=1")
        photo_info = requests.get(photo_request_url).content
        photo_result = json.loads(photo_info)['photo']

        if ('message' in photo_result):
            return jsonify(photo_result)

        photo_size_request_url = ("https://www.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=a729ddbdafe5c5dec056c2217ed488ce&"
        + "photo_id=" + photo_id + "&format=json&nojsoncallback=1")
        photo_size = requests.get(photo_size_request_url).content
        photo_size_result = json.loads(photo_size)
        
        if ('message' in photo_size_result):
            return jsonify(photo_size_result)

        largest = photo_size_result['sizes']['size'][-1]

        # - `id`: Flickr asset ID
        # - `created`: Date the asset was created, i.e. when the photo was taken or video was recorded
        # - `title`: The name the creator gave to the asset on Flickr (this might be blank for some assets)
        # - `width`: Width for the largest version of the asset
        # - `height`: Height for the largest version of the asset
        # - `url`: URL for the highest-resolution version of the asset
        photos_response.append({'id': photo_id, 'created': photo_result['dates']['posted'], 'title': photo['title'], 'width': largest['width'], 'height': largest['height'], 'url': largest['url']})
    
    return jsonify(photos_response)


@app.route('/download-assets', methods=['GET'])
def download_assets():

    if 'url' in request.args:
        url = request.args['url']
    else:
        return "Error: No Collection URL was provided"


    path_parts = url.split('/')
    user_id = path_parts[4]
    collection_id = path_parts[6]

    # Sample URL:
    # https://www.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key=a729ddbdafe5c5dec056c2217ed488ce&photoset_id=72157638428210105&user_id=11061732%40N07&format=json&nojsoncallback=1

    user_id = user_id.replace("@","%40")

    request_url = ("https://www.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key=a729ddbdafe5c5dec056c2217ed488ce&"
        + "photoset_id=" + collection_id + "&user_id=" + user_id + "&format=json&nojsoncallback=1")
    strlist = requests.get(request_url).content
    results = json.loads(strlist)

    if 'message' in results or 'photoset' not in results or 'photo' not in results['photoset']:
        return jsonify(results)

    for photo in results['photoset']['photo']:
        title = photo['title']
        photo_id = photo['id']

        photo_size_request_url = ("https://www.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=a729ddbdafe5c5dec056c2217ed488ce&"
        + "photo_id=" + photo_id + "&format=json&nojsoncallback=1")
        photo_size = requests.get(photo_size_request_url).content
        photo_size_result = json.loads(photo_size)
        if ('message' in photo_size_result):
            return jsonify(photo_size_result)
        largest_url = photo_size_result['sizes']['size'][-1]['source']
        ext = largest_url.split('.')[-1]

        folder_name = 'media'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        response = requests.get(largest_url)
        file = open(folder_name+"/"+str(photo_id)+"."+ext, "wb")
        file.write(response.content)
        file.close()
    
    return jsonify({ "Number of downloaded assets" : len(results['photoset']['photo'])})


app.run()