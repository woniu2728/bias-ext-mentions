from bias_ext_mentions.backend.events import UserMentionedEvent


def get_runtime_user_by_id(*args, **kwargs):
    from bias_core.extensions.runtime import get_runtime_user_by_id as runtime_get_user_by_id

    return runtime_get_user_by_id(*args, **kwargs)


def notify_runtime_notification(*args, **kwargs):
    from bias_core.extensions.runtime import notify_runtime_notification as runtime_notify_notification

    return runtime_notify_notification(*args, **kwargs)


def handle_user_mentioned_notification(event: UserMentionedEvent) -> None:
    mentioned_user = _resolve_user_or_none(event.mentioned_user_id)
    if mentioned_user is None:
        return

    from_user = _resolve_user_or_none(event.actor_user_id)
    if from_user is None:
        return

    notify_runtime_notification(
        "notify_user_mentioned_from_event",
        event=event,
        mentioned_user=mentioned_user,
        from_user=from_user,
    )


def _resolve_user_or_none(user_id: int):
    if not user_id:
        return None
    try:
        return get_runtime_user_by_id(user_id)
    except Exception:
        return None

