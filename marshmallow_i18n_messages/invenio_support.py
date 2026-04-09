# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CESNET z.s.p.o.
#
# marshmallow-i18n-messages is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""
Support for localization of InvenioRDM marshmallow messages.

This module is loaded as a part of an Invenio configuration

InvenioRDM imports and caches schema classes eagerly before Flask boots, so
calling :func:`~marshmallow_i18n_messages.patch_marshmallow.add_i18n_to_marshmallow`
from ``invenio.cfg`` arrives too late.  This finalizer re-patches the affected
schemas once the Flask app context and Invenio service registry are available
by calling :func:`~marshmallow_i18n_messages.patch_marshmallow.enable_i18n`
on each service schema.
"""

from typing import Any

from invenio_base.signals import app_loaded
from invenio_i18n import lazy_gettext

from marshmallow_i18n_messages import add_i18n_to_marshmallow, enable_i18n

# Add i18n support to marshmallow classes and validators
add_i18n_to_marshmallow(gettext_impl=lazy_gettext)


@app_loaded.connect
def app_loaded_signal(sender: Any, app: Any, **kwargs: Any) -> None:

    with app.app_context():
        import logging

        from invenio_records_resources.proxies import current_service_registry

        log = logging.getLogger("marshmallow_i18n_messages")

        _visited = set()
        for service in current_service_registry._services.values():
            service_config = getattr(service, "config", None)
            if not service_config:
                continue
            schema_cls = getattr(service_config, "schema", None)
            if not schema_cls:
                continue
            log.debug("Translating schema %s for service %s", schema_cls, service)
            enable_i18n(schema_cls, gettext_impl=lazy_gettext, _visited=_visited)
