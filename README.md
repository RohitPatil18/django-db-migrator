# Django Database Migrator

The **Django Database Migrator** is a simple utility written to seamlessly import data from one database to another within a Django application.

- **Column Transformations:** Easily manage scenarios where columns have been renamed, merged, or modified in the source database. 

- **Column Removal Handling:** When certain columns are no longer present in the source database, the utility gracefully handles this situation, preventing data loss or integrity issues.

- **Table Renaming:** If table names have changed, the utility accommodates these changes, ensuring a smooth transition of data.

- **Relational Data Management:** The utility takes care of maintaining relational data consistency during import, making sure that relationships between tables are preserved accurately.

## Features

- **Intuitive Configuration:** Configure the utility using simple settings to define source and target databases, mapping of columns, and other import-specific details.

- **Flexible Mapping:** Specify column mappings to adapt to changes in column names or structure, ensuring data is accurately transferred.

- **Data Transformation:** Apply custom data transformations during the import process, allowing you to modify data as needed before it's integrated into the target database.

- **Relational Handling:** The utility help identifies and manages relationships between tables, maintaining referential integrity in the target database.

- **Easy Integration:** Designed for seamless integration into existing Django projects.

## Contributing

I welcome contributions from the community! Whether you want to add features, improve documentation, or fix bugs, feel free to submit a pull request.