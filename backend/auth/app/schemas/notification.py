from pydantic import BaseModel
from auth.app.enums.notification import NotificationType


class NotificationSchema(BaseModel):
    type: NotificationType
    recipient: str
    payload: dict
