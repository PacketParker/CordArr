import datetime
import requests
import random
from wonderwords import RandomWord
from string import ascii_lowercase, digits

from utils.database import Session
from utils.models import JellyfinAccounts
from utils.config import (
    JELLYFIN_URL,
    JELLYFIN_HEADERS,
    ACCOUNT_TIME,
    SIMPLE_PASSWORDS,
)


def create_jellyfin_account(user_id):
    """
    Create a new Jellyfin account for the user and return the username and password

    Args:
        user_id (int): Discord user ID to create the account for

    Returns:
        tuple: The username and password of the new Jellyfin account
    """
    # Create username/password
    username = RandomWord().word(word_min_length=5, word_max_length=5)
    if SIMPLE_PASSWORDS:
        password = RandomWord().word(word_min_length=5, word_max_length=10)
    else:
        password = "".join(random.choices(ascii_lowercase + digits, k=15))

    deletion_time = datetime.datetime.now() + datetime.timedelta(
        minutes=ACCOUNT_TIME * 60
    )
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
        return False

    # Add the information to the database
    with Session() as session:
        session.add(
            JellyfinAccounts(
                user_id=user_id,
                jellyfin_user_id=jellyfin_user_id,
                deletion_time=deletion_time,
            )
        )
        session.commit()

    return username, password
