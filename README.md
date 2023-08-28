# Django Database Migrator

The **Django Database Migrator** is a simple utility written to seamlessly import data from one database to another within a Django application.

- **Column Transformations:** Easily manage scenarios where columns have been renamed, merged, or modified from the source database. 

- **Column Removal Handling:** When certain columns are no longer present in the source database, the utility gracefully handles this situation, preventing data loss or integrity issues.

- **Table Renaming:** If table names have changed, the utility accommodates these changes, ensuring a smooth transition of data.

- **Relational Data Management:** The utility takes care of maintaining relational data consistency during import, making sure that relationships between tables are preserved accurately.

## Features

- **Intuitive Configuration:** Configure the utility using simple settings to define source and target databases, mapping of columns, and other import-specific details.

- **Flexible Mapping:** Specify column mappings to adapt to changes in column names or structure, ensuring data is accurately transferred.

- **Data Transformation:** Apply custom data transformations during the import process, allowing you to modify data as needed before it's integrated into the target database.

- **Relational Handling:** The utility helps identify and manage relationships between tables, maintaining referential integrity in the target database.

- **Easy Integration:** Designed for seamless integration into existing Django projects.

## User Guide

### 1. Clone this Project
- Clone this repository on your local machine

### 2. Adding code to your project
- Create a new app (we are calling it `importer`) in your project using the following command:
  
    ```
    python manage.py startapp importer
    ```
- Inside the cloned directory, navigate to the core module where all the required files are kept. Copy them to your `importer` app and delete all unncessary files.


### 3. Configuring the Source Database

- Open the settings.py file in your Django project.
Locate the DATABASES section within the settings file.
- Configure the source database details. In this project, PostgreSQL is used as the source database. Modify the configuration according to your use case if needed. Make sure to use `source` key for your source database.

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("DATABASE_NAME"),
        "USER": env.str("DATABASE_USER"),
        "PASSWORD": env.str("DATABASE_PASSWORD"),
        "HOST": env.str("DATABASE_HOST"),
        "PORT": env("DATABASE_PORT"),
    },
    "source": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("SOURCE_DATABASE_NAME"),
        "USER": env.str("SOURCE_DATABASE_USER"),
        "PASSWORD": env.str("SOURCE_DATABASE_PASSWORD"),
        "HOST": env.str("SOURCE_DATABASE_HOST"),
        "PORT": env("SOURCE_DATABASE_PORT"),
    },
}
```
**Note:** In this example, environment variables to secure credentials and other confidential data.

### 4. Creating Mappers for Models
Mappers are essential for describing source and destination information and managing migrations.

- Inside your app's directory, Remove all code from `mappers.py`
- Define mappers for your models. Mappers provide clear details about migrations and how data will be transformed between the source and destination.
- For more detailed information about how to define mappers, refer to the [Defining Mappers](#defining-mappers) section of the project documentation.

### 5. Running scripts 
- Once all mappers are defined, create a list of mappers.
- Open shell using following command
    ```
    python manage.py shell
    ```
- Run following code to start importing data:
    ```python
    from importers.scripts import import_data
    from importers.mappers import mappers_list

    import_data(mappers_list)
    ```
- Make changes in following code as per your requirements.

Once script runs successfully, check your database.

<a name="defining-mappers"></a>
## Defining Mappers

To get better understanding, please refer to `demoapp/models.py` and [Previous models]((docs/another-file.md)
).

### Example 1

```python
class DeveloperMapper(BaseModelMap):
    destmodel = models.Developer
    sourcetable = "developer"
    exclude_fields = ["about"]

    status = MethodField()
    technology = ReferenceField(mapper=TechnologyMapper, source="technology_id")

    def get_status_value(self, row):
        if row["status"]:
            return models.DeveloperStatusChoice.active
        return models.DeveloperStatusChoice.inactive
```

In above example,
- **BaseModelMap:** Mapper needs to inherite this class to act as a mapper.
- **destmodel:** Current model in which data needs to be imported.
- **sourcetable:** Table name in old database from which data needs to be imported.
- **fields**: Usually, you do not need to mention any fields in your mapper if column properties match with your previous one or field is not a related field which refers to another column in different table (e.g. Foreign Key). But in case there are some modification in current models, you will need to define field as attribute where attribute name should match with field name.
  
  There are following types of fields available:
  - **Field:** 
    Use this class to define any field. 
    - `source`: Previous column name from where data needs to be imported
  - **ReferenceField:**
     Use this class for foreign key column.
     - `mapper`: Mapper for the reference table. In above example, we have added `technology` as reference field and used `TechnologyMapper` as mapper.
     - `source`: Previous column name from where data needs to be imported
  
  - **MethodField:**
    Use this class if data from the column needs to be modified. You also need to add a method which should follow given pattern for naming: `get_<fieldname>_value`. Replace `<fieldname>` by model field name.

    In above example, status column was changed from boolean to integer so we have defined a method where we have written logic to derive latest values.
- **exclude_fields:** List of columns which we want to ignore while importing the data. This could include columns which were not previously present in table.

### Example 2
```python
class TechnologyMapper(BaseModelMap):
    destmodel = models.Technology
    sourcetable = "mst_technology"
    renamed_columns = {"title": "name"}
```

In this example, we have added following additional attributes:
- **renamed_columns:** This dictionary provides the information of renamed columns where key should be field name in current model and value should be column name in old table.

## FAQ

### Is it necessary for both databases to be of the same type?
No. Even if both database are of different types it should work as long as both are SQL database. E.g. Your source database can be MySQL and destination database is PostgreSQL, It would work. Make sure to define proper database engine in `settings.py`


## Contributing

I welcome contributions from the community! Whether you want to add features, improve documentation, or fix bugs, feel free to submit a pull request.
