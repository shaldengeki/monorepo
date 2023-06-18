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
from ..fitbit_client import FitbitClient
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

    notification.processed_at = datetime.datetime.now().astimezone(timezone.utc)
    db.session.add(notification)
    db.session.commit()
    print(f"Subscription notification locked for processing: {notification.id}")

    return notification


def refresh_tokens_for_user(user: User, client: FitbitClient) -> User:
    data = client.refresh_user_tokens(user.fitbit_refresh_token)
    user.fitbit_access_token = data["access_token"]
    user.fitbit_refresh_token = data["refresh_token"]
    db.session.add(user)
    db.session.commit()
    print(f"Refreshed expired token for {user}.")

    return user


def fetch_user_activity_for_notification(
    notification: SubscriptionNotification,
    client: FitbitClient,
) -> dict:
    data = client.get_user_daily_activity_summary(
        notification.user.fitbit_user_id,
        notification.user.fitbit_access_token,
        notification.date,
    )
    if client.request_indicates_expired_token(data):
        notification.user = refresh_tokens_for_user(notification.user, client)
        return fetch_user_activity_for_notification(notification, client)

    return data


def process_subscription_notifications(client: FitbitClient) -> None:
    notification = maybe_fetch_subscription_notification()
    if notification is None:
        return

    try:
        # Fetch the user's activity for this date.
        activity = fetch_user_activity_for_notification(notification, client)
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
            or abs(float(last_activity.distance_km) - float(new_activity.distance_km))
            >= 0.01
        ):
            notification.user.synced_at = datetime.datetime.now().astimezone(
                timezone.utc
            )

            db.session.add(new_activity)
            db.session.add(notification.user)
            db.session.commit()
            print(f"Recorded new activity for {notification.user.fitbit_user_id}.")
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
        .where(SubscriptionNotification.processed_at == None)
        .values(processed_at=datetime.datetime.now().astimezone(timezone.utc))
    )
    db.session.execute(update_older_notifications)


max_delay = 10


def main() -> int:
    with app.app_context():
        client = app.config["FITBIT_CLIENT"]

        while True:
            start = time.time()
            process_subscription_notifications(client)
            delay = (start + max_delay) - time.time()
            if delay > 0:
                time.sleep(delay)


if __name__ == "__main__":
    raise SystemExit(main())
