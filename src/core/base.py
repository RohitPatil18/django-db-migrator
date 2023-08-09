import os

import pandas as pd

from . import fields
from .services import DatabaseExportService

DATASET = {}


class DatabaseExportModel:
    sourcetable = None

    def get_table_name(self):
        if not self.sourcetable:
            raise ValueError(
                "Add table name in inner Meta class (source: {0})".format(
                    self.__class__.__name__
                )
            )
        return self.sourcetable

    def export_to_csv(self):
        database_export_service = DatabaseExportService(tablename=self.get_table_name())
        database_export_service.export()


class BaseModelMap(DatabaseExportModel):
    destmodel = None
    sourcetable = None

    def get_method_value(self, value):
        return value

    def get_destmodel_fields(self):
        destfields = self.destmodel._meta._get_fields()
        fieldnames = {}
        for field in destfields:
            fieldtype = field.get_internal_type()
            if fieldtype in ("OneToOneField", "ForeignKey", "ManyToManyField"):
                continue
            fieldnames[field.name] = fields.Field(source=field.name)
        return fieldnames

    def get_deferred_fields(self):
        deferred_fields = {}
        attributes = vars(self.__class__)

        for attr, attrval in attributes.items():
            if isinstance(attrval, fields.Field):
                deferred_fields[attr] = attrval
        return deferred_fields

    def get_fields(self):
        fields = self.get_destmodel_fields()
        fields.update(self.get_deferred_fields())
        return fields

    def get_reference_field_val(self, field):
        if field.mapper.sourcetable not in DATASET:
            field.mapper().importdata()
        fk = DATASET[field.sourcetable]["pk"]
        return fk
    
    def add_to_dest_db(self, dataset):
        dest_objects = []
        for data in dataset:
            dest_objects.append(
                self.destmodel(
                    **data
                )
            )
        self.destmodel.objects.bulk_create(
            dest_objects,
            batch_size=100
        )
        

    def importdata(self, datadir=""):
        source_file_path = self.sourcetable + ".csv"
        if datadir != "":
            source_file_path = os.path.join(datadir, source_file_path)

        self.export_to_csv()
        df = pd.read_csv(source_file_path)

        modelfields = self.get_fields()

        dataset = []
        for _, row in df.iterrows():
            data = {}
            for field, fieldval in modelfields.items():
                data[field] = None
                if isinstance(fieldval, fields.MethodField):
                    method_name = f"get_{field}_value"
                    method = getattr(self, method_name)
                    data[field] = method(row)
                elif isinstance(fieldval, fields.ReferenceField):
                    data[field] = self.get_reference_field_val(fieldval)
                else:
                    data[field] = row[fieldval.source]
            dataset.append(data)

        self.add_to_dest_db(dataset)
