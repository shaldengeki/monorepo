from base64 import b64encode
import datetime
from datetime import timezone
import requests
from sqlalchemy import desc, update
from sqlalchemy.sql.functions import now
import time
from typing import Optional
from urllib.parse import urlencode

from ..config import app, db
from ..models import SubscriptionNotification, User, UserActivity


def maybe_fetch_subscription_notification() -> Optional[SubscriptionNotification]:
    # Lock a job, if it exists.
    notification = (
        SubscriptionNotification.query.filter(
            SubscriptionNotification.processed_at == None
        )
        .order_by(desc(SubscriptionNotification.created_at))
        .first()
    )

    if not notification:
        return None

    print(f"Subscription notification to process: {notification.id}")
    notification.processed_at = datetime.datetime.now().astimezone(timezone.utc)
    db.session.add(notification)
    db.session.commit()
    print(f"Notification locked.")

    return notification


def fetch_user_for_notification(
    notification: SubscriptionNotification,
) -> Optional[User]:
    return User.query.filter(User.fitbit_user_id == notification.fitbit_user_id).first()


def request_indicates_expired_token(response: dict) -> bool:
    return "errors" in response and any(
        e["errorType"] == "expired_token" for e in response["errors"]
    )


def refresh_tokens_for_user(user: User, client_id: str, client_secret: str) -> User:
    encoded_client_and_secret = b64encode(
        f"{client_id}:{client_secret}".encode("utf-8")
    ).decode("utf-8")

    url_parameters = urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": user.fitbit_refresh_token,
        }
    )

    response = requests.post(
        "https://api.fitbit.com/oauth2/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_client_and_secret}",
        },
        data=url_parameters,
    )

    if response.status_code not in (200, 201):
        raise ValueError(f"Error when refreshing user tokens: {response.json()}")

    data = response.json()
    user.fitbit_access_token = data["access_token"]
    user.fitbit_refresh_token = data["refresh_token"]
    db.session.add(user)
    db.session.commit()

    return user


def fetch_user_activity_for_notification(
    notification: SubscriptionNotification,
    user: User,
    client_id: str,
    client_secret: str,
) -> dict:
    formatted_date: str = notification.date.strftime("%Y-%m-%d")
    print(f"Fetching {notification.fitbit_user_id}'s activity for {formatted_date}.")
    data = requests.get(
        f"https://api.fitbit.com/1/user/{notification.fitbit_user_id}/activities/date/{formatted_date}.json",
        headers={"Authorization": f"Bearer {user.fitbit_access_token}"},
    ).json()

    if request_indicates_expired_token(data):
        print(f"Refreshing expired token.")
        user = refresh_tokens_for_user(user, client_id, client_secret)
        print(
            f"Fetching {notification.fitbit_user_id}'s activity for {formatted_date}."
        )
        data = requests.get(
            f"https://api.fitbit.com/1/user/{notification.fitbit_user_id}/activities/date/{formatted_date}.json",
            headers={"Authorization": f"Bearer {user.fitbit_access_token}"},
        ).json()

    return data


def process_subscription_notifications(client_id: str, client_secret: str) -> None:
    notification = maybe_fetch_subscription_notification()
    if notification is None:
        print("No subscription notifications to process, skipping.")
        return

    try:
        # Fetch the user's activity for this date.
        user = fetch_user_for_notification(notification)
        if user is None:
            print(
                f"No user found for notification {notification}, marking as done and skipping."
            )
            notification.processed_at = datetime.datetime.now().astimezone(timezone.utc)
            db.session.add(notification)
            db.session.commit()
            return None
        activity = fetch_user_activity_for_notification(
            notification, user, client_id, client_secret
        )
        active_minutes: int = (
            activity["summary"]["veryActiveMinutes"]
            + activity["summary"]["fairlyActiveMinutes"]
            + activity["summary"]["lightlyActiveMinutes"]
        )
        distance_km = sum(
            [
                x["distance"]
                for x in activity["summary"]["distances"]
                if x["activity"] == "total"
            ]
        )

        new_activity = UserActivity(
            record_date=notification.date.date(),
            user=notification.fitbit_user_id,
            steps=activity["summary"]["steps"],
            active_minutes=active_minutes,
            distance_km=distance_km,
        )
        last_activity = (
            UserActivity.query.filter(
                UserActivity.record_date == notification.date.date()
            )
            .filter(UserActivity.user == notification.fitbit_user_id)
            .order_by(desc(UserActivity.created_at))
            .first()
        )
        if not last_activity or (
            last_activity.steps != new_activity.steps
            or last_activity.active_minutes != new_activity.active_minutes
            or last_activity.distance_km != new_activity.distance_km
        ):
            user.synced_at = datetime.datetime.now().astimezone(timezone.utc)

            print(f"Recording new activity.")
            db.session.add(new_activity)
            db.session.add(user)
            db.session.commit()
        else:
            print(f"No new activity logged, skipping.")
    except:
        notification.processed_at = None
        db.session.add(notification)
        db.session.commit()
        raise

    # Mark all older notifications than this one as done, too.
    update_older_notifications = (
        update(SubscriptionNotification)
        .where(SubscriptionNotification.fitbit_user_id == notification.fitbit_user_id)
        .where(SubscriptionNotification.date == notification.date)
        .where(SubscriptionNotification.created_at <= notification.created_at)
        .values(processed_at=datetime.datetime.now().astimezone(timezone.utc))
    )
    db.session.execute(update_older_notifications)


max_delay = 10


def main() -> int:
    with app.app_context():
        client_id = app.config["FITBIT_CLIENT_ID"]
        client_secret = app.config["FITBIT_CLIENT_SECRET"]

        while True:
            start = time.time()
            process_subscription_notifications(client_id, client_secret)
            delay = (start + max_delay) - time.time()
            if delay > 0:
                print(f"Sleeping for {round(delay)} seconds")
                time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
