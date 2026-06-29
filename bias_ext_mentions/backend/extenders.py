from __future__ import annotations

from bias_core.extensions import (
    AdminSurfaceExtender,
    ApiResourceExtender,
    ConditionalExtender,
    EventListenersExtender,
    FormatterExtender,
    ForumCapabilitiesExtender,
    LifecycleExtender,
    ModelExtender,
    PostLifecycleExtender,
    ServiceProviderExtender,
)

from bias_ext_mentions.backend.admin_surface import permission_definitions
from bias_ext_mentions.backend.constants import POST_MODEL
from bias_ext_mentions.backend.formatter import render_mentions_html
from bias_ext_mentions.backend.frontend import frontend_extender
from bias_ext_mentions.backend.lifecycle import (
    apply_post_approved_mentions,
    apply_post_created_mentions,
    apply_post_hidden_mentions,
    apply_post_updated_mentions,
    prepare_post_delete_mentions,
)
from bias_ext_mentions.backend.listener_contracts import mention_event_listener_definitions
from bias_ext_mentions.backend.model_contracts import owned_models, post_model_relationships
from bias_ext_mentions.backend.notification_contracts import notification_extender
from bias_ext_mentions.backend.resource_contracts import user_detail_resource_field_definitions
from bias_ext_mentions.backend.resources import post_mentions_preload_resolver
from bias_ext_mentions.backend.runtime import mention_service_provider
from bias_ext_mentions.backend.search_contracts import search_filter_definitions
from bias_ext_mentions.backend.tag_contracts import tag_mentions_extenders


def frontend_extenders():
    return (frontend_extender(),)


def admin_extenders():
    return (
        AdminSurfaceExtender(
            permissions=permission_definitions(),
            permissions_pages=("/admin/extensions/mentions/permissions",),
        ),
    )


def forum_extenders():
    return (
        ForumCapabilitiesExtender(
            search_filters=search_filter_definitions(),
        ),
    )


def event_extenders():
    return (
        PostLifecycleExtender().handler(
            "mentions",
            apply_created=apply_post_created_mentions,
            apply_updated=apply_post_updated_mentions,
            apply_approved=apply_post_approved_mentions,
            apply_hidden=apply_post_hidden_mentions,
            prepare_delete=prepare_post_delete_mentions,
            description="帖子可见性变化与生命周期变更时维护提及关系并派发提及事件。",
        ),
    )


def notification_integration_extenders():
    return (
        notification_extender(),
        EventListenersExtender(
            listeners=mention_event_listener_definitions(),
        ),
    )


def optional_integration_extenders():
    return (
        ConditionalExtender().when_extension_enabled("notifications", notification_integration_extenders),
    )


def formatting_extenders():
    return (
        FormatterExtender(transforms=(render_mentions_html,)),
        ConditionalExtender().when_extension_enabled("tags", tag_mentions_extenders),
    )


def model_extenders():
    extender = ModelExtender(model=POST_MODEL)
    for model, description in owned_models():
        extender = extender.owns(model, description=description)
    for relationship in post_model_relationships():
        extender = extender.belongs_to_many(
            relationship["name"],
            relationship["model"],
            resolver=relationship["resolver"],
            description=relationship["description"],
        )
    return (extender,)


def resource_extenders():
    return (
        ApiResourceExtender("post").model_relationship(
            "mentionsUsers",
            resource_type="user_summary",
            many=True,
            description="帖子中被提及的用户摘要列表。",
            preload_resolver=post_mentions_preload_resolver,
        ),
        ApiResourceExtender("user_detail").fields(user_detail_resource_field_definitions),
    )


def service_extenders():
    return (
        ServiceProviderExtender(
            key="mentions.service",
            provider=mention_service_provider,
        ),
        LifecycleExtender(),
    )
