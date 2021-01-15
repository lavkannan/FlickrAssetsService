import flask
from flask import request, jsonify
import requests
import json


app = flask.Flask(__name__)
app.config["DEBUG"] = True


# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Flickr Reader Service</h1>
            <p>Try '/collections-metadata'</p>'''


@app.route('/collections-metadata', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
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
        largest = photo_size_result['sizes']['size'][-1]

        if ('message' in photo_size_result):
            return jsonify(photo_size_result)

        # - `id`: Flickr asset ID
        # - `created`: Date the asset was created, i.e. when the photo was taken or video was recorded
        # - `title`: The name the creator gave to the asset on Flickr (this might be blank for some assets)
        # - `width`: Width for the largest version of the asset
        # - `height`: Height for the largest version of the asset
        # - `url`: URL for the highest-resolution version of the asset
        photos_response.append({'id': photo_id, 'created': photo_result['dates']['posted'], 'title': photo['title'], 'width': largest['width'], 'height': largest['height'], 'url': largest['url']})
    
    return jsonify(photos_response)


app.run()