from __future__ import annotations

from bias_ext_mentions.backend.constants import POST_MODEL, USER_MODEL
from bias_ext_mentions.backend.models import PostMentionsUser
from bias_ext_mentions.backend.resources import resolve_post_mentions_user_models


def owned_models():
    return (
        (
            PostMentionsUser,
            "帖子提及用户关系由 mentions 扩展拥有。",
        ),
    )


def post_model_relationships():
    return (
        {
            "name": "mentionsUsers",
            "model": USER_MODEL,
            "resolver": resolve_post_mentions_user_models,
            "description": "帖子中被提及的用户模型关系。",
        },
    )
