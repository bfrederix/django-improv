class APIObject(object):

    def __init__(self, model_instance, **kwargs):
        self.update_fields(model_instance)

    def update_fields(self, model_instance):
        for field in self.field_list:
            attr_value = getattr(model_instance, field)
            if attr_value is not None:
                setattr(self, field, attr_value)