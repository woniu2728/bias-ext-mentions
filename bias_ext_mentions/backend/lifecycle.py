from bias_core.extensions.platform import dispatch_forum_event_after_commit
from bias_ext_mentions.backend.events import UserMentionedEvent
from bias_ext_mentions.backend.models import PostMentionsUser
from bias_ext_mentions.backend.parser import extract_mentioned_usernames


def delete_runtime_user_mentioned_notifications_for_post(*args, **kwargs):
    from bias_core.extensions.runtime import (
        delete_runtime_user_mentioned_notifications_for_post as runtime_delete_user_mentioned_notifications_for_post,
    )

    return runtime_delete_user_mentioned_notifications_for_post(*args, **kwargs)


def list_runtime_users_by_usernames(*args, **kwargs):
    from bias_core.extensions.runtime import list_runtime_users_by_usernames as runtime_list_users_by_usernames

    return runtime_list_users_by_usernames(*args, **kwargs)


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
    mentioned_users = list_runtime_users_by_usernames(mentions)
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
    deleted_count = 0
    for user_id in user_ids:
        deleted_count += delete_runtime_user_mentioned_notifications_for_post(
            post_id,
            mentioned_user_id=user_id,
        )
    return deleted_count

