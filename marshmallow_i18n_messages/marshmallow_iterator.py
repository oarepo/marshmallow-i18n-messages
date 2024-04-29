import inspect


class MarshmallowIterator:

    def classes(self):

        import marshmallow
        import marshmallow_utils.fields
        import marshmallow_utils.schemas

        def is_marshmallow_class(member):
            return issubclass(member, (marshmallow.fields.Field, marshmallow.Schema))

        yield from iter_module(marshmallow, is_marshmallow_class)
        yield from iter_module(marshmallow.fields, is_marshmallow_class)
        yield from iter_module(marshmallow_utils, is_marshmallow_class)
        yield from iter_module(marshmallow_utils.fields, is_marshmallow_class)
        yield from iter_module(marshmallow_utils.schemas, is_marshmallow_class)

    def validators(self):
        import marshmallow
        import marshmallow.validate

        def is_marshmallow_validator(member):
            return issubclass(member, marshmallow.validate.Validator)

        yield from iter_module(marshmallow.validate, is_marshmallow_validator)


def iter_module(python_module, condition):
    for name in dir(python_module):
        if name.startswith("__"):
            continue
        member = getattr(python_module, name)
        if inspect.ismodule(member):
            if member.__name__.startswith(python_module.__name__):
                yield from iter_module(member, condition)
        elif inspect.isclass(member):
            full_name = f"{member.__module__}.{member.__name__}"
            if full_name.startswith(python_module.__name__) and condition(member):
                yield member
