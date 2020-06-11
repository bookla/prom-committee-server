from google.cloud import storage
import os
import shutil
from PIL import Image

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'MY CRED'


def clear_temp():
    folder = 'PATH TO TEMP'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def create_thumbnails():
    client = storage.Client()
    bucket = client.get_bucket("prom-b3bc9.appspot.com")
    blobs = list(bucket.list_blobs())
    files = {}
    thumbnails = {}
    for each_blob in blobs:
        if "@" not in each_blob.id and each_blob.id.count("/") > 2 and "@thumbnails" not in each_blob.id:
            files[each_blob.id.replace("prom-b3bc9.appspot.com/", "").split("/")[1]] = each_blob
        elif "@thumbnails" in each_blob.id:
            thumbnails[each_blob.id.replace("prom-b3bc9.appspot.com/", "").split("/")[1]] = each_blob

    for each_file in files.keys():
        if each_file in thumbnails.keys():
            print("Skipping thumbnail already exists")
        else:
            print("Thumbnail for " + each_file + " was not found, creating one!")
            temp_name = "PATH TO TEMP" + each_file
            with open(temp_name, "wb") as temp_file:
                files[each_file].download_to_file(temp_file)
                temp_file.close()

            image = Image.open(temp_name)
            width, height = image.size
            scale = height/400
            image.thumbnail((width/scale, height/scale))
            image.save(temp_name, format=image.format)

            with open(temp_name, "rb") as temp_read:
                upload_target = bucket.blob("@thumbnails/" + each_file)
                upload_target.upload_from_file(temp_read)
                upload_target.make_public()
            print("Thumbnail for " + each_file + " created successfully")
    clear_temp()
