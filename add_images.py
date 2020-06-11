from google.cloud import firestore, storage
import os
from os.path import isfile, join
import random
import string

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'MY CRED'


def add(target: str, append: bool):
    db = firestore.Client()
    collection = db.collection(u'students')
    client = storage.Client()
    bucket = client.get_bucket("prom-b3bc9.appspot.com")

    upload_path = "/Users/book/PycharmProjects/work/to_upload/"
    upload_files = [f for f in os.listdir(upload_path) if isfile(join(upload_path, f))]

    print("SECURITY: service account added images will generate a key coded public link. Sensitive information like password hash data should be uploaded through a more secure service account or through Firebase clients.")

    print("Fetching images from the upload folder.")
    url_list = []
    for each_file in upload_files:
        file_uid = "serviceAdd-" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        remote_filename = target.replace(" ", "") + "/" + file_uid + "." + each_file.split(".")[1]
        upload_target = bucket.blob(remote_filename)
        file_path = join(upload_path, each_file)
        if ".ds_store" in each_file.lower() :
            continue
        with open(file_path, "rb") as imgRead:
            upload_target.upload_from_file(imgRead)
            upload_target.make_public()
            url_list.append(upload_target.public_url)
            print("Uploaded " + each_file + " to " + remote_filename)
    user_doc = collection.document(target.lower())
    current_document = user_doc.get().to_dict()
    if not append:
        input("OVERWRITE? : Press [ENTER] to overwrite existing image data.")
        new_document = current_document
        new_document["updateData"]["imageLinks"] = url_list
        print(new_document)
        user_doc.update(new_document)
    else:
        input("OVERFLOW WARNING : The system will not check if there are more than 10 images, this may cause overflow in the form updater program. Press [ENTER] to continue")
        current_data = current_document["updateData"]["imageLinks"]
        new_data = current_data + url_list
        new_document = current_document
        new_document["updateData"]["imageLinks"] = new_data
        print(new_document)
        user_doc.update(new_document)
    print("User Data Updated")
    db.collection("requests").document("client-students").update({"requiresUpdate": True})
    print("Form update request submitted, Google Sheets will update to reflect the change shortly.")


add(target=input("Name of student: "), append=True)


