import inspect
from gettext import gettext
from threading import Lock

from speaklater import make_lazy_gettext

from marshmallow_i18n_messages.marshmallow_iterator import MarshmallowIterator

from marshmallow import fields, ValidationError


def _lazy_gettext(*args, **kwargs):
    return make_lazy_gettext(lambda: gettext)(*args, **kwargs)


add_i18n_to_marshmallow_called = False
add_i18n_to_marshmallow_lock = Lock()


def add_i18n_to_marshmallow(gettext_impl=_lazy_gettext):
    global add_i18n_to_marshmallow_called
    if add_i18n_to_marshmallow_called:
        return
    patch_all_classes(gettext_impl)
    add_i18n_to_marshmallow_called = True

    def patch_make_error(previous_make_error):
        def apply_kwargs(inst, param, **kwargs):
            if isinstance(param, dict):
                for k, v in list(param.items()):
                    param[k] = apply_kwargs(inst, v, **kwargs)
            elif isinstance(param, list):
                for i, v in enumerate(param):
                    param[i] = apply_kwargs(inst, v, **kwargs)
            return str(param).format(**kwargs)

        def make_error_i18n(self: fields.Field, key: str, **kwargs) -> ValidationError:
            error = previous_make_error(self, key, **kwargs)
            error.messages = apply_kwargs(self, error.messages, **kwargs)
            return error

        return make_error_i18n

    # monkey patch make error
    fields.Field.make_error = patch_make_error(fields.Field.make_error)


def patch_all_classes(gettext_impl):
    with add_i18n_to_marshmallow_lock:
        for clz in MarshmallowIterator().classes():
            patch_class(clz, gettext_impl)
        for clz in MarshmallowIterator().validators():
            patch_validator(clz, gettext_impl)


def patch_class(clz, gettext_impl):
    if hasattr(clz, "error_messages"):
        for k, v in clz.error_messages.items():
            if isinstance(v, str):
                clz.error_messages[k] = gettext_impl(v)
    if hasattr(clz, "default_error_messages"):
        for k, v in clz.default_error_messages.items():
            if isinstance(v, str):
                clz.default_error_messages[k] = gettext_impl(v)
    if hasattr(clz, "default_message"):
        if isinstance(clz.default_message, str):
            clz.default_message = gettext_impl(clz.default_message)
    if hasattr(clz, "default_error_message"):
        if isinstance(clz.default_error_message, str):
            clz.default_error_message = gettext_impl(clz.default_error_message)
    if hasattr(clz, "validators"):
        patch_validators(clz.validators, gettext_impl)


def patch_validators(validators, gettext_impl):
    if not validators:
        return
    if not isinstance(validators, list):
        validators = [validators]
    for validator in validators:
        patch_validator(validator, gettext_impl)


def patch_validator(validator, gettext_impl):
    patch_class(validator, gettext_impl)
    # special handling for validator properties
    if hasattr(validator, 'message'):
        if isinstance(validator.message, str):
            validator.message = gettext_impl(validator.message)
    for name, attr in inspect.getmembers(validator):
        if name.startswith("message_"):
            if isinstance(attr, str):
                setattr(validator, name, gettext_impl(attr))
