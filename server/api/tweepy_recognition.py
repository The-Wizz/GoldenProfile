import tweepy
import urllib.request
import urllib.parse
import urllib.error
import face_recognition
import os
from flask import jsonify
from .tweepy_connection_helper import initialize_api


def get_twitter(input_first_name, input_last_name, input_email, input_path_to_known_picture):

    api = initialize_api()

    users = api.search_users(input_first_name + " " + input_last_name)

    found_user = None

    known_image = face_recognition.load_image_file(
        "./uploads/" + input_path_to_known_picture)
    known_faces = face_recognition.face_encodings(known_image)

    for current_searching_user in users:
        print("current user: " + current_searching_user.name)

        url = current_searching_user.profile_image_url

        url = url.replace('_normal', '')

        path_to_unknown_picture = input_first_name + "-" + \
            input_last_name + "-" + "twitter" + ".jpg"

        urllib.request.urlretrieve(url, path_to_unknown_picture)
        unknown_image = face_recognition.load_image_file(
            path_to_unknown_picture)

        is_done = False
        for recognized_face_know_face in known_faces:
            print("isdone: " + str(is_done))
            if is_done:
                break
            for recognized_face_unknown_face in face_recognition.face_encodings(unknown_image):
                result = face_recognition.compare_faces(
                    [recognized_face_know_face], recognized_face_unknown_face)
                if result:
                    print("result: " + str(result))
                    found_user = current_searching_user
                    is_done = True
                    break

    print(found_user)
    root_download_path = "./twitter-downloads/"
    counter = 0
    output_data = {}
    if found_user:
        tweets = list()
        media_files = list()
        posted_tweets = api.user_timeline(found_user.id_str, count=1000)
        for status in posted_tweets:
            if len(tweets) <= 100:
                tweets.append(status.text)
            media = status.entities.get('media', [])
            if(len(media) > 0):
                media_files.append(media[0]['media_url'])
                path_to_download = root_download_path + input_first_name + \
                    "-" + input_last_name + "-" + str(counter) + ".jpg"
                print("")
                print("")
                print(path_to_download)
                print("")
                print("")
                urllib.request.urlretrieve(
                    media[0]['media_url'], path_to_download)
                counter += 1
                was_not_found = True
                for known_face in known_faces:
                    try:
                        unknown_image = face_recognition.load_image_file(
                            path_to_download)
                    except IOError:
                        break
                    unknown_faces = face_recognition.face_encodings(
                        unknown_image)
                    for unknown_face in unknown_faces:
                        result = face_recognition.compare_faces(
                            [known_face], unknown_face)
                        if True in result:
                            was_not_found = False
                if was_not_found:
                    os.remove(path_to_download)
                    media_files.remove(media[0]['media_url'])
                print(str(len(media_files)))
                if len(media_files) is 20:
                    print("maximum of 20 reached")
                    break

        output_data['number_of_followers'] = found_user.followers_count
        output_data['link_to_profile_picture'] = found_user.profile_image_url.replace(
            '_normal', '')
        output_data['profile_description'] = found_user.description
        output_data['location'] = found_user.location
        output_data['creation_date'] = found_user.created_at
        output_data['linkToProfile'] = found_user.url
        output_data['linksToPictures'] = media_files
        output_data['tweets'] = tweets
        for tw in tweets:
            print("tweets: " + tw)
    return output_data
