from base import DATASET
from .mappers import mappers_list

def import_data(mappers_list):
    print("Import process started...")

    for Mapper in mappers_list:
        mapper = Mapper()
        print("-----------------------------------------")
        print(f"Importing data from {mapper.sourcetable}...")
        if DATASET.get(mapper.sourcetable, {}) == {}:
            mapper.importdata()
        
        objects = mapper.destmodel.objects.all()

        dictionary = {}
        for obj in objects:
            dictionary[obj.pk] = obj
        DATASET[mapper.sourcetable] = dictionary

    print("-----------------------------------------")
    print("-----------------------------------------")
    print("Import process completed.")

import_data(mappers_list)