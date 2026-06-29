from __future__ import annotations

from bias_core.extensions import SearchFilterDefinition

from bias_ext_mentions.backend.constants import EXTENSION_ID
from bias_ext_mentions.backend.search import (
    apply_post_mentioned_me_search_filter,
    parse_mentioned_me_search_filter,
)


def search_filter_definitions():
    return (
        SearchFilterDefinition(
            code="mentioned_me",
            label="提及我的回复",
            module_id=EXTENSION_ID,
            target="post",
            parser=parse_mentioned_me_search_filter,
            applier=apply_post_mentioned_me_search_filter,
            syntax="mentioned:me",
            description="仅返回提及当前用户的回复。",
        ),
    )
