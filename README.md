# FlickrAssetsService

## Introduction 
This is a web service for retrieving information about and downloading images from Flickr given a URL.

## Instructions
1. Install Flask if needed
2. Run 'python flickr_service.py'
3. This should print a local URL you can use to access this service (Example: Running on http://127.0.0.1:5000/)
4. Try the collections metadata endpoint (Example: http://127.0.0.1:5000/collections-metadata?url=https://www.flickr.com/photos/11061732@N07/collections/72157638428210105/)
5. Try the asset downloads endpoint (Example: http://127.0.0.1:5000/download-assets?url=https://www.flickr.com/photos/11061732@N07/collections/72157638428210105/)


## Implementation decisions
### Flask
I chose to use Flask because this is a great out-of-the box Python web service framework for quick tasks such as this.

### Tradeoffs
My implementation currently performs the most basic solution for retrieving a list of images given a collection or album ID, and retrieve individual image info or URL for every image in that list. Since this does take a few seconds, this implementation could be improved in the future by adding UI support for a progress bar or buffering symbol.
