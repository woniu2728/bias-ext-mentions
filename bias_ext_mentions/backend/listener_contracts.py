from __future__ import annotations

from bias_core.extensions import ExtensionEventListenerDefinition

from bias_ext_mentions.backend.events import UserMentionedEvent
from bias_ext_mentions.backend.listeners import handle_user_mentioned_notification


def mention_event_listener_definitions():
    return (
        ExtensionEventListenerDefinition(
            event_type=UserMentionedEvent,
            handler=handle_user_mentioned_notification,
            description="用户被提及时派发提及通知。",
        ),
    )
