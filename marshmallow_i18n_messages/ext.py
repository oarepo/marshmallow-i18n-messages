class MarshmallowI18nMessagesExt:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        from marshmallow_i18n_messages import add_i18n_to_marshmallow
        add_i18n_to_marshmallow()