from __future__ import annotations

from bias_core.extensions import NotificationsExtender


def notification_extender():
    return (
        NotificationsExtender()
        .type(
            "userMentioned",
            label="@提及通知",
            description="通知用户其在回复中被提及。",
            icon="fas fa-at",
            navigation_scope="post",
            preference_key="notify_user_mentioned",
            preference_label="@提及通知",
            preference_description="当其他用户在回复中提及你时通知你。",
        )
    )
