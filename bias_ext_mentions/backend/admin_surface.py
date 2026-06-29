from __future__ import annotations

from bias_core.extensions import PermissionDefinition

from bias_ext_mentions.backend.constants import EXTENSION_ID


def permission_definitions():
    return (
        PermissionDefinition(
            code="mentionGroups",
            label="提及用户组",
            section="posting",
            section_label="发帖",
            module_id=EXTENSION_ID,
            icon="fas fa-at",
            description="允许用户在回复中提及用户组。",
        ),
    )
