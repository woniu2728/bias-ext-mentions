from bias_ext_mentions.backend.extenders import (
    admin_extenders,
    event_extenders,
    formatting_extenders,
    forum_extenders,
    frontend_extenders,
    model_extenders,
    optional_integration_extenders,
    resource_extenders,
    service_extenders,
)


def extend():
    return [
        *frontend_extenders(),
        *admin_extenders(),
        *forum_extenders(),
        *event_extenders(),
        *optional_integration_extenders(),
        *formatting_extenders(),
        *model_extenders(),
        *resource_extenders(),
        *service_extenders(),
    ]
