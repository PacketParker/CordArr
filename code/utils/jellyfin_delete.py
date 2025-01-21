import datetime
import sqlite3
import requests

from utils.config import JELLYFIN_URL, JELLYFIN_HEADERS


def delete_accounts():
    """
    Delete Jellyfin accounts that have passed their deletion time
    """
    # Get all expired Jellyfin accounts
    db = sqlite3.connect("data/cordarr.db")
    cursor = db.cursor()
    cursor.execute(
        "SELECT jellyfin_user_id FROM jellyfin_accounts WHERE"
        " deletion_time < ?",
        (datetime.datetime.now(),),
    )
    jellyfin_user_ids = cursor.fetchall()

    # Delete the Jellyfin accounts
    for jellyfin_user_id in jellyfin_user_ids:
        request = requests.delete(
            f"{JELLYFIN_URL}/Users/{jellyfin_user_id[0]}",
            headers=JELLYFIN_HEADERS,
        )
        # If 204 - account deleted
        # If 404 - account not found
        # Either way, remove account from database
        if request.status_code in (404, 204):
            cursor.execute(
                "DELETE FROM jellyfin_accounts WHERE jellyfin_user_id = ?",
                (jellyfin_user_id,),
            )

    db.commit()
    db.close()
