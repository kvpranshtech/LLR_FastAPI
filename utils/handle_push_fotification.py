import os

import requests
from celery import shared_task
from django.utils import timezone
from django.conf import Settings
from django.contrib.auth.models import User
# FCM_SERVER_KEY = Settings.FCM_SERVER_KEY
FCM_SERVER_KEY = "YOUR_FCM_SERVER_KEY"
from firebase_admin import messaging, credentials
import firebase_admin


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIREBASE_CRED_PATH = os.path.join(BASE_DIR, "firebase", "landlineremover-aaefb-firebase-adminsdk-fbsvc-09d24f27fc.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)

#


# def send_push_notification(token, title, body):
#     headers = {
#         "Authorization": f"key={FCM_SERVER_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "to": token,
#         "notification": {
#             "title": title,
#             "body": body,
#         },
#         "data": {  # extra payload if needed
#             "click_action": "FLUTTER_NOTIFICATION_CLICK",
#             "notification_id": str(timezone.now().timestamp()),
#         }
#     }
#     print(f"----to{token} ---- title::{title} ---- body :: { body }")
    # response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, json=data)
    # return response.json()



# @shared_task
# def send_bulk_site_notifications_task(user_ids, title, description):
#     users = User.objects.filter(id__in=user_ids).prefetch_related("device_tokens")
#     print("List of all users --------", users)
#     for user in users:
#         for device in user.device_tokens.all():
#             if device.device_token:  # only if device has token
#                 print("Has device token -------",device.device_token )
#                 send_push_notification(device.device_token, title, description or "")



def send_push_notification(token, title, body, notification_type, file_id=None):

    data = {
        "click_action": "FLUTTER_NOTIFICATION_CLICK",
        "notification_id": str(timezone.now().timestamp()),
        "notification_type": notification_type
    }

    if file_id:
        data["file_id"] = str(file_id)

    print("Notification type----", notification_type, "---- file-id---", file_id)
    # Add custom type if provided
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,  # FCM device token
        data=data,
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                channel_id='default_channel_id',
                sound='default',
                notification_count=1,
            ),
        ),
        apns=messaging.APNSConfig(
            headers={
                "apns-priority": "10",
            },
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound="default",
                    badge=1,
                    content_available=True,
                ),
            ),
        ),

    )

    try:
        response = messaging.send(message)
        print(f"✅ Successfully sent message for '{title}':", response)
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"❌ Error sending message for '{title}':", str(e), "FCM Token :", token)
        return {"status": "error", "message": str(e)}


@shared_task
def send_bulk_site_notifications_task(user_ids, title, description, notification_type):
    users = User.objects.filter(id__in=user_ids).prefetch_related("device_data")
    print("List of all users --------", users)

    for user in users:
        for device in user.device_data.all():  # updated relation
            if device.device_token:  # only if device has token
                print(f"Has device token ------- {device.device_token}")
                send_push_notification(
                    token=device.device_token,
                    title=title,
                    body=description or "",
                    notification_type=notification_type,

                )

