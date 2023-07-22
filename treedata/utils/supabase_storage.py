import logging

import requests


def check_file_exists_in_supabase_storage(supabase_url, supabase_bucket_name, file_name):
    url = f'{supabase_url}/storage/v1/object/info/public/{supabase_bucket_name}/{file_name}'
    response = requests.get(url)
    return response.status_code == 200


def upload_file_to_supabase_storage(supabase_url, supabase_bucket_name, supabase_role_key, file_path, file_name):
    try:
        file = open(file_path, 'rb')
        file_url = f'{supabase_url}/storage/v1/object/{supabase_bucket_name}/{file_name}'
        r = requests.put if check_file_exists_in_supabase_storage(supabase_url, supabase_bucket_name,
                                                                  file_name) else requests.post
        response = r(
            file_url,
            files={'file': file},
            headers={
                'Authorization': f'Bearer {supabase_role_key}',
                'ContentType': 'application/geo+json',
                'AcceptEncoding': 'gzip, deflate, br'
            },
        )
        if response.status_code == 200:
            logging.info("✅ Uploaded {} to supabase storage".format(file_name))
        else:
            logging.warning(response.status_code)
            logging.warning(response.content)
            logging.warning("❌ Could not upload {} to supabase storage".format(file_name))
    except Exception as error:
        logging.warning(error)
        logging.warning("❌ Could not upload {} supabase storage".format(file_name))


def upload_files_to_supabase_storage(supabase_url, supabase_bucket_name, supabase_role_key, file_path_to_file_name):
    for file_path in file_path_to_file_name:
        upload_file_to_supabase_storage(
            supabase_url=supabase_url,
            supabase_bucket_name=supabase_bucket_name,
            supabase_role_key=supabase_role_key,
            file_path=file_path,
            file_name=file_path_to_file_name[file_path]
        )
