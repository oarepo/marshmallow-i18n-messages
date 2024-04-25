# marshmallow-i18n-messages

A simple library to provide i18n messages for marshmallow validation errors.

## Installation

```python
from marshmallow_i18n_messages import add_i18n_to_marshmallow

add_i18n_to_marshmallow()
```

## Usage

After the initialization above, all marshmallow validation errors will be translated to the current babel
locale.

## Invenio usage

In Invenio, just using the library is enough. It will be automatically used when invenio boots up.

## Contributing new translations

To contribute new translations/fix translation issues:

1. Fork the repository and create a feature branch
2. Add your language to build.sh script and create an empty `messages.po` 
   in the `marshmallow_i18n_messages/translations/<language>/LC_MESSAGES` directory
3. Run the build.sh script
4. Translate the messages in the generated .po file
5. Run the build.sh script again
6. Commit the changes, push to your fork and create a pull request
