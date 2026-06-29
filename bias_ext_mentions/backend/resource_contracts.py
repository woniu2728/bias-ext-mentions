from __future__ import annotations

from bias_core.extensions import ResourceFieldDefinition
from bias_core.extensions.runtime import has_runtime_forum_permission

from bias_ext_mentions.backend.constants import EXTENSION_ID


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
    return bool(actor and has_runtime_forum_permission(actor, "mentionGroups"))


def _visible_to_self(user, context: dict) -> bool:
    actor = context.get("user")
    return bool(actor and actor.is_authenticated and user and actor.id == user.id)
