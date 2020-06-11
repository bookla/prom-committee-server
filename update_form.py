from google.cloud import firestore
import prom_form_updater
import prom_vote_loader
import sponsor_form_updater
import generate_thumbnails
import datetime
import os
import time

update_freq_hours = 0.5

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'MY CRED'

db = firestore.Client()


def check_for_update():
    requests = db.collection('requests')
    student_requests = requests.document('client-students')
    student_update_data = student_requests.get().to_dict()
    if student_update_data["requiresUpdate"]:
        print("Update for student responses requested")
        print("\nGenerating thumbnails for new images: ")
        generate_thumbnails.create_thumbnails()
        print("\nUpdating responses:")
        prom_form_updater.main()
        print("\nUpdating votes:")
        prom_vote_loader.load_and_print_votes(mute=True)
        print("\n"*20)
        reset_update_status(u"client-students")
    time.sleep(1)
    sponsor_requests = requests.document(u'client-sponsor')
    sponsor_update_data = sponsor_requests.get().to_dict()
    if sponsor_update_data["requiresUpdate"]:
        print("Update for sponsor responses requested")
        sponsor_form_updater.main()
        print("\n" * 20)
        reset_update_status(u"client-sponsor")


def reset_update_status(for_type: str):
    requests = db.collection(u'requests')
    update_requests = requests.document(for_type)
    reset_data = {"requiresUpdate": False}
    update_requests.update(reset_data)
    print("Successfully updated : " + for_type)


def start():
    while True:
        print("Checking for updates")
        print(datetime.datetime.now())
        check_for_update()
        time.sleep(10)


start()
