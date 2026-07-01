from __future__ import annotations

from bias_core.extensions import ResourceFieldDefinition

from bias_ext_mentions.backend.constants import EXTENSION_ID


def get_user_service():
    from bias_core.extensions.runtime import get_runtime_service

    return get_runtime_service("users.service")


def _service_method(service, name: str):
    if isinstance(service, dict):
        method = service.get(name)
    else:
        method = getattr(service, name, None)
    if not callable(method):
        raise RuntimeError(f"Mentions 扩展运行时服务缺少方法: {name}")
    return method


def user_detail_resource_field_definitions():
    return (
        ResourceFieldDefinition(
            resource="user_detail",
            field="canMentionGroups",
            module_id=EXTENSION_ID,
            resolver=resolve_user_can_mention_groups,
            description="当前用户是否可以提及用户组。",
            visible=_visible_to_self,
        ),
    )


def resolve_user_can_mention_groups(user, context: dict) -> bool:
    actor = context.get("user")
    return bool(actor and _service_method(get_user_service(), "has_forum_permission")(actor, "mentionGroups"))


def _visible_to_self(user, context: dict) -> bool:
    actor = context.get("user")
    return bool(actor and actor.is_authenticated and user and actor.id == user.id)
