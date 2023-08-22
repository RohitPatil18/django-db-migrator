import os

import pandas as pd
import numpy as np

from . import fields
from .services import DatabaseExportService

DATASET = {}


class DatabaseExportModel:
    sourcetable = None

    def get_table_name(self):
        """
        Returns table name from where data needs to be extracted.
        """
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
    """
    Base model map which can be inherited create a mapper for any entity.
    """

    destmodel = None
    sourcetable = None
    exclude_fields = []
    renamed_columns = {}

    def __init__(self):
        self._check_required_attributes()

    def _check_required_attributes(self):
        assert self.destmodel is None, (
            "'%s' should include a `destmodel` attribute" % self.__class__.__name__
        )

        assert self.sourcetable is None, (
            "'%s' should include a `sourcetable` attribute" % self.__class__.__name__
        )

    def get_destmodel_fields(self):
        """
        Returns list of fields of model.
        """
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

    def get_reference_field_val(self, name, field, row):
        if field.mapper.sourcetable not in DATASET:
            field.mapper().importdata()
            try:
                objects = field.mapper.destmodel.all_objects.all()
            except:
                objects = field.mapper.destmodel.objects.all()
            dictionary = {}
            for obj in objects:
                dictionary[obj.pk] = obj
            DATASET[field.mapper.sourcetable] = dictionary
        key = row.get(field.source)

        if key:
            fk = DATASET[field.mapper.sourcetable].get(key)
            if not fk:
                """@TODO: Handle this condition."""
                print(key)
            return fk
        return None

    def add_to_dest_db(self, dataset):
        dest_objects = []
        for data in dataset:
            dest_objects.append(self.destmodel(**data))
        self.destmodel.objects.bulk_create(
            dest_objects,
            batch_size=1000,
        )

    def importdata(self, datadir=""):
        source_file_path = self.sourcetable + ".csv"
        if datadir != "":
            source_file_path = os.path.join(datadir, source_file_path)

        self.export_to_csv()
        df = pd.read_csv(source_file_path)

        modelfields = self.get_fields()

        dataset = []
        skip = False
        for i, row in df.iterrows():
            data = {}
            for field, fieldval in modelfields.items():
                data[field] = None
                if field in self.exclude_fields:
                    continue
                elif field in self.renamed_columns:
                    key = self.renamed_columns[field]
                    value = row.get(key)
                    data[field] = value
                elif isinstance(fieldval, fields.MethodField):
                    method_name = f"get_{field}_value"
                    method = getattr(self, method_name)
                    data[field] = method(row)
                elif isinstance(fieldval, fields.ReferenceField):
                    data[field] = self.get_reference_field_val(
                        field,
                        fieldval,
                        row,
                    )
                    if not data[field]:
                        skip = True
                else:
                    value = row.get(fieldval.source)

                    if not value:
                        try:
                            value = df[i][fieldval.source]
                        except:
                            """
                            @TODO: Handle this condition
                            """
                            pass
                    data[field] = value

                if isinstance(data[field], float) and np.isnan(data[field]):
                    data[field] = None
            if not skip:
                dataset.append(data)
        self.add_to_dest_db(dataset)
