import datetime
import requests

from utils.database import Session
from utils.models import JellyfinAccounts
from utils.config import LOG, JELLYFIN_URL, JELLYFIN_HEADERS


def delete_accounts():
    """
    Delete Jellyfin accounts that have passed their deletion time
    """
    # Get all expired Jellyfin accounts
    with Session() as session:
        jellyfin_user_ids = (
            session.query(JellyfinAccounts.jellyfin_user_id)
            .filter(JellyfinAccounts.deletion_time < datetime.datetime.now())
            .all()
        )

        # Delete each account
        for jellyfin_user_id in jellyfin_user_ids:
            print(f"Deleting account {jellyfin_user_id[0]}")
            try:
                response = requests.delete(
                    f"{JELLYFIN_URL}/Users/{jellyfin_user_id[0]}",
                    headers=JELLYFIN_HEADERS,
                )
                response.raise_for_status()
                # Get the account and delete it
                account = (
                    session.query(JellyfinAccounts)
                    .filter(
                        JellyfinAccounts.jellyfin_user_id
                        == jellyfin_user_id[0]
                    )
                    .first()
                )
                session.delete(account)
            except:
                LOG.error(
                    "Failed deleting Jellyfin account w/ ID"
                    f" {jellyfin_user_id[0]}"
                )
        # Commit changes
        session.commit()
