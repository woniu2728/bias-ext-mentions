from bias_ext_mentions.backend.events import UserMentionedEvent


def get_runtime_service(service_key: str, default=None):
    from bias_core.extensions.runtime import get_runtime_service as runtime_get_service

    return runtime_get_service(service_key, default)


def _service_method(service, name: str, *, required: bool = True):
    if isinstance(service, dict):
        method = service.get(name)
    else:
        method = getattr(service, name, None)
    if callable(method):
        return method
    if required:
        raise RuntimeError(f"Mentions 扩展运行时服务缺少方法: {name}")
    return None


def _call_notification(method_name: str, **kwargs):
    service = get_runtime_service("notifications.service")
    method = _service_method(service, method_name, required=False) if service is not None else None
    if method is not None:
        return method(**kwargs)


def handle_user_mentioned_notification(event: UserMentionedEvent) -> None:
    mentioned_user = _resolve_user_or_none(event.mentioned_user_id)
    if mentioned_user is None:
        return

    from_user = _resolve_user_or_none(event.actor_user_id)
    if from_user is None:
        return

    _call_notification(
        "notify_user_mentioned_from_event",
        event=event,
        mentioned_user=mentioned_user,
        from_user=from_user,
    )


def _resolve_user_or_none(user_id: int):
    if not user_id:
        return None
    try:
        return _service_method(get_runtime_service("users.service"), "get_by_id")(user_id)
    except Exception:
        return None

