from bias_core.extensions.platform import dispatch_forum_event_after_commit
from bias_ext_mentions.backend.events import UserMentionedEvent
from bias_ext_mentions.backend.models import PostMentionsUser
from bias_ext_mentions.backend.parser import extract_mentioned_usernames


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


def apply_post_created_mentions(*, post, context: dict | None = None, **kwargs) -> dict:
    content = (context or {}).get("content", post.content)
    mentioned_user_ids = _sync_post_mentions(post, content, replace_existing=False)
    return {"mentioned_user_ids": mentioned_user_ids}


def apply_post_updated_mentions(*, post, context: dict | None = None, **kwargs) -> dict:
    content = (context or {}).get("content", post.content)
    mentioned_user_ids = _sync_post_mentions(post, content, replace_existing=True)
    return {"mentioned_user_ids": mentioned_user_ids}


def apply_post_approved_mentions(*, post, context: dict | None = None, **kwargs) -> dict:
    content = (context or {}).get("content", post.content)
    mentioned_user_ids = _sync_post_mentions(post, content, replace_existing=True)
    return {"mentioned_user_ids": mentioned_user_ids}


def apply_post_hidden_mentions(*, post, context: dict | None = None, **kwargs) -> dict:
    if (context or {}).get("is_hidden"):
        mentioned_user_ids = _current_mentioned_user_ids(post.id)
        deleted_count, _ = PostMentionsUser.objects.filter(post_id=post.id).delete()
        notification_deleted_count = _delete_mention_notifications(post.id, mentioned_user_ids)
        return {
            "mentioned_user_ids": (),
            "deleted_count": deleted_count,
            "notification_deleted_count": notification_deleted_count,
        }

    content = (context or {}).get("content", post.content)
    mentioned_user_ids = _sync_post_mentions(post, content, replace_existing=True)
    return {"mentioned_user_ids": mentioned_user_ids}


def prepare_post_delete_mentions(*, post, context: dict | None = None, **kwargs) -> dict:
    mentioned_user_ids = _current_mentioned_user_ids(post.id)
    if mentioned_user_ids:
        PostMentionsUser.objects.filter(post_id=post.id).delete()
        _delete_mention_notifications(post.id, mentioned_user_ids)
    return {"mentioned_user_ids": mentioned_user_ids}


def _sync_post_mentions(post, content: str, *, replace_existing: bool) -> tuple[int, ...]:
    previous_user_ids = _current_mentioned_user_ids(post.id) if replace_existing else ()
    if replace_existing:
        PostMentionsUser.objects.filter(post_id=post.id).delete()

    mentions = extract_mentioned_usernames(content)
    if not mentions:
        _delete_mention_notifications(post.id, previous_user_ids)
        return ()

    mentioned_user_ids: list[int] = []
    mentioned_users = _service_method(get_runtime_service("users.service"), "list_by_usernames")(mentions)
    for mentioned_user in mentioned_users:
        _, created = PostMentionsUser.objects.get_or_create(
            post_id=post.id,
            mentions_user=mentioned_user,
        )
        mentioned_user_ids.append(mentioned_user.id)

        if created:
            dispatch_forum_event_after_commit(
                UserMentionedEvent(
                    post_id=post.id,
                    discussion_id=post.discussion_id,
                    actor_user_id=post.user_id,
                    mentioned_user_id=mentioned_user.id,
                    post_number=post.number,
                    discussion_title=getattr(getattr(post, "discussion", None), "title", "") or "",
                )
            )

    resolved_user_ids = tuple(mentioned_user_ids)
    removed_user_ids = tuple(sorted(set(previous_user_ids) - set(resolved_user_ids)))
    _delete_mention_notifications(post.id, removed_user_ids)
    return resolved_user_ids


def _current_mentioned_user_ids(post_id: int) -> tuple[int, ...]:
    return tuple(PostMentionsUser.objects.filter(post_id=post_id).values_list("mentions_user_id", flat=True))


def _delete_mention_notifications(post_id: int, user_ids: tuple[int, ...]) -> int:
    service = get_runtime_service("notifications.service")
    delete_for_post = _service_method(service, "delete_user_mentioned_for_post", required=False) if service is not None else None
    if delete_for_post is None:
        return 0

    deleted_count = 0
    for user_id in user_ids:
        deleted_count += delete_for_post(
            post_id,
            mentioned_user_id=user_id,
        )
    return deleted_count

