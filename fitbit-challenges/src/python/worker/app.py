import requests
from sqlalchemy import desc, update
from sqlalchemy.sql.functions import now
import time
from typing import Optional

from ..config import app, db
from ..models import SubscriptionNotification, User, UserActivity


def maybe_fetch_subscription_notification() -> Optional[SubscriptionNotification]:
    # Lock a job, if it exists.
    notification = (
        SubscriptionNotification.query.filter(
            SubscriptionNotification.processed_at is None
        )
        .order_by(desc(SubscriptionNotification.created_at))
        .first()
    )

    if not notification:
        return None

    print(f"Subscription notification to process: {notification.id}")
    notification.processed_at = now
    db.session.add(notification)
    db.session.commit()
    print(f"Notification locked.")

    return notification


def fetch_user_for_notification(
    notification: SubscriptionNotification,
) -> Optional[User]:
    return User.query.filter(User.fitbit_user_id == notification.fitbit_user_id).first()


def fetch_user_activity_for_notification(
    notification: SubscriptionNotification,
) -> dict:
    formatted_date: str = notification.date.strftime("%Y-%m-%d")
    user = fetch_user_for_notification(notification)
    if user is None:
        return []

    print(f"Fetching {notification.fitbit_user_id}'s activity for {formatted_date}.")
    data = requests.get(
        f"https://api.fitbit.com/1/user/{notification.fitbit_user_id}/activities/date/{formatted_date}.json",
        headers={"Authorization": f"Bearer {user.fitbit_access_token}"},
    ).json()
    print(f"Fetched data: {data}")
    return data


def process_subscription_notifications() -> None:
    notification = maybe_fetch_subscription_notification()
    if notification is None:
        print("No subscription notifications to process, skipping.")
        return

    try:
        # Fetch the user's activity for this date.
        activity = fetch_user_activity_for_notification(notification)
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

        print(f"Recording new activity: {new_activity}")
        db.session.add(new_activity)
        db.session.commit()
    except:
        notification.processed_at = None
        db.session.add(notification)
        db.session.commit()
        raise


max_delay = 10


def main() -> int:
    with app.app_context():
        while True:
            start = time.time()
            process_subscription_notifications()
            delay = (time.time() + max_delay) - start
            if delay > 0:
                print(f"Sleeping for {round(delay)} seconds")
                time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
