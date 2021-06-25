# For using listdir()
import os
import csv

import logging
import boto3
from botocore.exceptions import ClientError


# replace the value of this variable
# with the absolute path of the directory
walk_dir = '/home/felipe/Documents/PhD/forro em vinil resampled'
map_file_path = 'covers.csv'

count = 0

S3 = boto3.resource('s3', aws_access_key_id='', aws_secret_access_key='')

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL':'public-read'})
    except ClientError as e:
        logging.error(e)
        return False
    return True


with open(map_file_path, 'a') as map_file:
    fieldnames = ['file_path', 'url']
    writer = csv.DictWriter(map_file, fieldnames=fieldnames)
    writer.writeheader()
    for root, dirs, files in os.walk(walk_dir):
            path = root.split(os.sep)
            remote_path = [item for item in path if item not in walk_dir.split('/')]
            for file in files:
                if ".jpeg" in file or ".jpg" in file or ".png" in file or ".JPG" in file or ".PNG" in file or ".JPEG" in file:
                # if ".mp3" in file or ".wma" in file or ".MP3" in file or ".WMA" in file:
                    bucket_name = 'forro-em-vinil-covers'
                    object_name = os.path.join(root, file).replace('/home/felipe/Documents/PhD/forro em vinil resampled/', '')
                    upload_file(
                        os.path.join(root, file),
                        bucket_name,
                        object_name=object_name)
                    count += 1
                    # print("file %i of %i (%.2f%%)" % (count, 27352, (count/27352) * 100))
                    print("picture number %i stored" % count)
                    writer.writerow({
                        "file_path": os.path.join(root, file),
                        "url": "https://%s.s3.amazonaws.com/%s" % (bucket_name, object_name)
                    })
