import requests
import json
import logging


def get_mapbox_s3_data(mapbox_username, mapbox_token):
    url = f"https://api.mapbox.com/uploads/v1/{mapbox_username}/credentials?access_token={mapbox_token}"
    response = requests.post(url)
    s3_credentials = json.loads(response.content)
    return {
        "aws_access_key_id": s3_credentials["accessKeyId"],
        "aws_secret_access_key": s3_credentials["secretAccessKey"],
        "aws_session_token": s3_credentials["sessionToken"],
        "bucket_name": s3_credentials["bucket"],
        "file_name": s3_credentials["key"]
    }


def notify_mapbox_upload(mapbox_username, mapbox_token, mapbox_s3_bucket_name, mapbox_s3_file_name, mapbox_tileset):
    url = f"https://api.mapbox.com/uploads/v1/{mapbox_username}?access_token={mapbox_token}"
    # assuming tileset = <mapboxusername>.<tilesetname>
    payload_dict = {
        "url": f"http://{mapbox_s3_bucket_name}.s3.amazonaws.com/{mapbox_s3_file_name}",
        "tileset": mapbox_tileset
    }
    payload = json.dumps(payload_dict)
    headers = {
        'content-type': 'application/json',
        'Accept-Charset': 'UTF-8',
        'Cache-Control': 'no-cache'
    }
    response = requests.post(url, data=payload, headers=headers)
    logging.info(f"Updated mapbox with response: {response}")
