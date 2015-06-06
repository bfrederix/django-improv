from django.db import models
from django.db.models import ForeignKey


class BoundedBigIntegerField(models.BigIntegerField):
    description = "Big Integer"

    MAX_VALUE = 9223372036854775807

    def get_internal_type(self):
        return "BigIntegerField"

    def get_prep_value(self, value):
        if value:
            value = long(value)
            assert value <= self.MAX_VALUE
        return super(BoundedBigIntegerField, self).get_prep_value(value)

class BoundedBigAutoField(models.AutoField):
    description = "Big Integer"

    MAX_VALUE = 9223372036854775807

    def db_type(self, connection):
        engine = connection.settings_dict['ENGINE']
        if 'mysql' in engine:
            return "bigint AUTO_INCREMENT"
        elif 'oracle' in engine:
            return "NUMBER(19)"
        elif 'postgres' in engine:
            return "bigserial"
        # SQLite doesnt actually support bigints with auto incr
        elif 'sqlite' in engine:
            return 'integer'
        else:
            raise NotImplemented

    def get_related_db_type(self, connection):
        return BoundedBigIntegerField().db_type(connection)

    def get_internal_type(self):
        return "BigIntegerField"

    def get_prep_value(self, value):
        if value:
            value = long(value)
            assert value <= self.MAX_VALUE
        return super(BoundedBigAutoField, self).get_prep_value(value)


class FlexibleForeignKey(ForeignKey):
    def db_type(self, connection):
        # This is required to support BigAutoField (or anything similar)
        rel_field = self.related_field
        if hasattr(rel_field, 'get_related_db_type'):
            return rel_field.get_related_db_type(connection)
        return super(FlexibleForeignKey, self).db_type(connection)
