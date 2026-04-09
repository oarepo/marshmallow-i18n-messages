# marshmallow-i18n-messages

A simple library to provide i18n messages for marshmallow validation errors.

## Installation

```shell
pip install marshmallow-i18n-messages
```

## Usage

Call `add_i18n_to_marshmallow` once at application startup, **before** any
marshmallow schemas are imported or instantiated:

```python
from marshmallow_i18n_messages import add_i18n_to_marshmallow

add_i18n_to_marshmallow()
```

After this call all marshmallow validation errors will be translated to the
active GNU gettext locale at the moment the error is rendered.

## Enabling i18n for schemas loaded before `add_i18n_to_marshmallow`

If a schema class was imported and cached **before** `add_i18n_to_marshmallow`
was called, its error messages will not have been wrapped yet.  Enable i18n on
it explicitly with `enable_i18n`:

```python
from marshmallow_i18n_messages import enable_i18n

enable_i18n(MyAlreadyLoadedSchema)
```

`enable_i18n` is idempotent — calling it on a schema that is already
patched is safe and has no effect.  It also recurses into parent classes and
any nested schemas automatically.

## Invenio / InvenioRDM usage

This package ships with an integrated support for InvenioRDM repositories 
and in most cases, no extra configuration is necessary to activate the translations.

This package adds an `invenio_config.module` entrypoint that is loaded
when InvenioRDM configuration is loaded. This entrypoint:

* Calls `add_i18n_to_marshmallow(lazy_gettext)` with the `lazy_gettext` from `invenio_i18n`
* Registers an `app_loaded` signal. In this signal it processes marshmallow schemas from
  all registered invenio services which might have been already cached before the 
  `add_i18n_to_marshmallow` was called.


If you encounter a schema that is neither covered by the global patch above
nor by the built-in service-schema finalizer, patch it explicitly in
`invenio.cfg`:

```python
from mypackage import MyUncoveredSchema
from marshmallow_i18n_messages import enable_i18n
from invenio_i18n import lazy_gettext

enable_i18n(MyUncoveredSchema, lazy_gettext)
```

If you find such a gap in the built-in coverage, please open an issue so it
can be addressed in a future release.

## Contributing new translations

To contribute new translations or fix translation issues:

1. Fork the repository and create a feature branch.
2. Add your language to `build.sh` and create an empty `messages.po` file at
   `marshmallow_i18n_messages/translations/<language>/LC_MESSAGES/messages.po`.
3. Run `build.sh` to regenerate the POT template and merge it into your PO
   file.
4. Translate the messages in the generated `.po` file.
5. Run `build.sh` again to compile the translations.
6. Commit the changes, push to your fork, and open a pull request.
