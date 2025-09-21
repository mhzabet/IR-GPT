class ArchiveRouter:
    """
    Routes MessageArchive model to 'archive' DB and others to 'default'
    """
    route_app_labels = {'archive'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'archive'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'archive'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # allow relations if both objects are in the same DB
        if (
            obj1._meta.app_label in self.route_app_labels and
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        elif (
            obj1._meta.app_label not in self.route_app_labels and
            obj2._meta.app_label not in self.route_app_labels
        ):
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'archive'
        return db == 'default'