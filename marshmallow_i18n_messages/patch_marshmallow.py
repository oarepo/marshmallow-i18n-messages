from gettext import gettext

from speaklater import make_lazy_gettext, _LazyString

from marshmallow_i18n_messages.marshmallow_iterator import MarshmallowIterator

from marshmallow import fields, ValidationError


def lazy_gettext(*args, **kwargs):
    return make_lazy_gettext(lambda: gettext)(*args, **kwargs)


def add_i18n_to_marshmallow():
    for clz in MarshmallowIterator().classes():
        if hasattr(clz, "error_messages"):
            for k, v in clz.error_messages.items():
                clz.error_messages[k] = lazy_gettext(v)
        if hasattr(clz, "default_error_messages"):
            for k, v in clz.default_error_messages.items():
                clz.default_error_messages[k] = lazy_gettext(v)
        if hasattr(clz, "default_message"):
            clz.default_message = lazy_gettext(clz.default_message)
        if hasattr(clz, "default_error_message"):
            clz.default_error_message = lazy_gettext(clz.default_error_message)

    def patch_make_error(previous_make_error):
        def apply_kwargs(param, **kwargs):
            if isinstance(param, _LazyString):
                return str(param).format(**kwargs)
            elif isinstance(param, dict):
                for k, v in list(param.items()):
                    param[k] = apply_kwargs(v, **kwargs)
            elif isinstance(param, list):
                for i, v in enumerate(param):
                    param[i] = apply_kwargs(v, **kwargs)
            return param

        def make_error_i18n(self: fields.Field, key: str, **kwargs) -> ValidationError:
            error = previous_make_error(self, key, **kwargs)
            error.messages = apply_kwargs(error.messages, **kwargs)
            return error
        return make_error_i18n


    # monkey patch make error
    fields.Field.make_error = patch_make_error(fields.Field.make_error)