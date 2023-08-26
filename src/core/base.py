import os
from typing import Any, List

import numpy as np
import pandas as pd
from pandas.core.series import Series

from . import fields
from .services import BACKUP_DIR, DatabaseExportService

DATASET = (
    {}
)  # Instead of storing data here, prefer another storage option for large data.


class DatabaseExportModel:
    sourcetable = None

    def get_table_name(self) -> str:
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

    def export_to_csv(self) -> None:
        database_export_service = DatabaseExportService(tablename=self.get_table_name())
        database_export_service.export()


class BaseModelMap(DatabaseExportModel):
    """
    Base model mapper which can be inherited create a mapper for any entity.
    """

    destmodel = None
    sourcetable = None
    exclude_fields = []
    renamed_columns = {}

    def __init__(self) -> None:
        self._check_required_attributes()

    def _check_required_attributes(self) -> None:
        assert self.destmodel is None, (
            "'%s' should include a `destmodel` attribute" % self.__class__.__name__
        )

        assert self.sourcetable is None, (
            "'%s' should include a `sourcetable` attribute" % self.__class__.__name__
        )

    def get_destmodel_fields(self) -> dict:
        """
        Returns list of fields from current model (where data needs to be added).
        It skips any relational field from the model.
        """
        destfields = self.destmodel._meta._get_fields()
        fieldnames = {}
        for field in destfields:
            fieldtype = field.get_internal_type()
            if fieldtype in ("OneToOneField", "ForeignKey", "ManyToManyField"):
                continue
            fieldnames[field.name] = fields.Field(source=field.name)
        return fieldnames

    def get_deferred_fields(self) -> dict:
        """
        Returns a dictionary of fields which are explicitly mentioned
        in model mapper.
        """
        deferred_fields = {}
        attributes = vars(self.__class__)

        for attr, attrval in attributes.items():
            if isinstance(attrval, fields.Field):
                deferred_fields[attr] = attrval
        return deferred_fields

    def get_fields(self) -> dict:
        """
        Returns list of fields from the destination model as well as fields
        that are explicitly mentioned in the mapper. (excludes relational fields)
        """
        fields = self.get_destmodel_fields()
        fields.update(self.get_deferred_fields())
        return fields

    def get_reference_field_val(
        self,
        field: fields.ReferenceField,
        row: Series,
    ) -> Any:
        """
        Extract value for the reference field from related table.
        We searched in `DATASET` for the data, if not found we make
        sure to prepopulate data in retated table and the retrieve the
        foreign key data for current table.
        """
        if field.mapper.sourcetable not in DATASET:
            field.mapper().importdata()
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

    def add_to_dest_db(self, dataset: List[dict]) -> None:
        dest_objects = []
        for data in dataset:
            dest_objects.append(self.destmodel(**data))
        self.destmodel.objects.bulk_create(
            dest_objects,
            batch_size=1000,
        )

    def get_source_file_path(self, datadir: str) -> str:
        """
        Returns source file path
        """
        source_file_path = self.sourcetable + ".csv"
        if datadir != "":
            source_file_path = os.path.join(datadir, source_file_path)
        else:
            source_file_path = os.path.join(BACKUP_DIR, source_file_path)
        return source_file_path

    def importdata(self, datadir=""):
        """
        This is main method of this class that needs to be called to
        start import process.
        """
        source_file_path = self.get_source_file_path(datadir)

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
                    data[field] = value

                if isinstance(data[field], float) and np.isnan(data[field]):
                    data[field] = None
            if not skip:
                dataset.append(data)
        self.add_to_dest_db(dataset)
