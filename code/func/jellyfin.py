import datetime
import requests
import random
import string
import sqlite3

from global_variables import JELLYFIN_URL, JELLYFIN_HEADERS, ACCOUNT_TIME

"""
Create a new Jellyfin account for the user and return the username and password
"""


def create_jellyfin_account(user_id):
    username = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    password = "".join(random.choices(string.ascii_lowercase + string.digits, k=15))

    deletion_time = datetime.datetime.now() + datetime.timedelta(hours=ACCOUNT_TIME)
    # Create the new Jellyfin account
    request_1 = requests.post(
        f"{JELLYFIN_URL}/Users/New",
        headers=JELLYFIN_HEADERS,
        json={"Name": username, "Password": password},
    )
    if request_1.status_code != 200:
        return False

    # Get the user ID of the new account
    jellyfin_user_id = request_1.json()["Id"]
    # Get the account policy and make edits
    request_2 = requests.get(
        f"{JELLYFIN_URL}/Users/{jellyfin_user_id}", headers=JELLYFIN_HEADERS
    )
    if request_2.status_code != 200:
        return False

    account_policy = request_2.json()
    account_policy["Policy"]["SyncPlayAccess"] = "JoinGroups"
    account_policy["Policy"]["EnableContentDownloading"] = False
    account_policy["Policy"]["InvalidLoginAttemptCount"] = 3
    account_policy["Policy"]["MaxActiveSessions"] = 1
    # Update the user with the newly edited policy
    request_3 = requests.post(
        f"{JELLYFIN_URL}/Users?userId={jellyfin_user_id}",
        headers=JELLYFIN_HEADERS,
        json=account_policy,
    )
    if request_3.status_code != 204:
        print(request_3.json())
        print(request_3.status_code)
        print("BROKEN AT REQUEST 3")
        return False

    # Add the information to the database
    db = sqlite3.connect("cordarr.db")
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO jellyfin_accounts (user_id, jellyfin_user_id, deletion_time) VALUES (?, ?, ?)",
        (user_id, jellyfin_user_id, deletion_time),
    )
    db.commit()
    db.close()

    return username, password