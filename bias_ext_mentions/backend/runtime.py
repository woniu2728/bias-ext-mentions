from __future__ import annotations


def mention_service_provider() -> dict:
    from bias_ext_mentions.backend.models import PostMentionsUser

    return {
        "model": PostMentionsUser,
    }


def require_extension_host_service(*args, **kwargs):
    from bias_core.extensions.runtime import require_extension_host_service as runtime_require_extension_host_service

    return runtime_require_extension_host_service(*args, **kwargs)


def get_post_mention_model():
    service = require_extension_host_service("mentions.service")
    model = service.get("model") if isinstance(service, dict) else getattr(service, "model", None)
    if model is None:
        raise RuntimeError("mentions.service 未提供提及关系模型")
    return model


