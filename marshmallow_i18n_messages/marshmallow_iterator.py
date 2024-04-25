import inspect


class MarshmallowIterator:

    def classes(self):
        def iter_module(python_module):
            for name in dir(python_module):
                if name.startswith("__"):
                    continue
                member = getattr(python_module, name)
                if inspect.ismodule(member):
                    if member.__name__.startswith(python_module.__name__):
                        yield from iter_module(member)
                elif inspect.isclass(member):
                    full_name = f"{member.__module__}.{member.__name__}"
                    if full_name.startswith(python_module.__name__):
                        yield member

        import marshmallow
        import marshmallow_utils.fields
        import marshmallow_utils.schemas

        yield from iter_module(marshmallow)
        yield from iter_module(marshmallow.fields)
        yield from iter_module(marshmallow_utils)
        yield from iter_module(marshmallow_utils.fields)
        yield from iter_module(marshmallow_utils.schemas)
