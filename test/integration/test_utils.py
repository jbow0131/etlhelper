"""Tests for utils functions."""
import pytest

from etlhelper.exceptions import ETLHelperQueryError
from etlhelper.utils import Column, describe_columns

# pylint: disable=unused-argument, missing-docstring


def test_describe_columns_no_schema_no_duplicates(pgtestdb_conn, pgtestdb_test_tables):
    # Arrange
    expected = [
        Column('id', 'integer'),
        Column('value', 'double precision'),
        Column('simple_text', 'text'),
        Column('utf8_text', 'text'),
        Column('day', 'date'),
        Column('date_time', 'timestamp without time zone')
    ]

    # Act
    columns = describe_columns('src', pgtestdb_conn)

    # Assert
    assert columns == expected


def test_describe_columns_with_schema_no_duplicates(pgtestdb_conn, pgtestdb_test_tables):
    # Arrange
    expected = [
        Column('id', 'integer'),
        Column('value', 'double precision'),
        Column('simple_text', 'text'),
        Column('utf8_text', 'text'),
        Column('day', 'date'),
        Column('date_time', 'timestamp without time zone')
    ]

    # Act
    columns = describe_columns('src', pgtestdb_conn, schema='public')

    # Assert
    assert columns == expected


def test_describe_columns_no_schema_with_duplicates(pgtestdb_conn, duplicate_schema):
    # Arrange, act and assert
    with pytest.raises(ETLHelperQueryError, match=r'Table name src is not unique'):
        describe_columns('src', pgtestdb_conn)


def test_describe_columns_with_schema_with_duplicates(pgtestdb_conn, duplicate_schema):
    # Arrange
    expected = [
        Column('id', 'integer'),
        Column('value', 'double precision'),
        Column('simple_text', 'text'),
        Column('utf8_text', 'text'),
        Column('day', 'date'),
        Column('date_time', 'timestamp without time zone')
    ]

    # Act
    columns = describe_columns('src', pgtestdb_conn, schema='public')

    # Assert
    assert columns == expected


def test_describe_columns_bad_table_name_no_schema(pgtestdb_conn, pgtestdb_test_tables):
    # Arrange, act and assert
    with pytest.raises(ETLHelperQueryError, match=r"Table name 'bad_table' not found."):
        describe_columns('bad_table', pgtestdb_conn)


def test_describe_columns_bad_table_name_with_schema(pgtestdb_conn, pgtestdb_test_tables):
    # Arrange, act and assert
    with pytest.raises(ETLHelperQueryError, match=r"Table name 'public.bad_table' not found."):
        describe_columns('bad_table', pgtestdb_conn, schema='public')


# Fixtures here

@pytest.fixture(scope='function')
def duplicate_schema(pgtestdb_conn, pgtestdb_test_tables):
    # Set up
    with pgtestdb_conn.cursor() as cursor:
        # Create a duplicate of the test tables in a new schema
        cursor.execute("CREATE SCHEMA IF NOT EXISTS duplicate", pgtestdb_conn)
        cursor.execute("SELECT * INTO duplicate.src FROM src", pgtestdb_conn)
    pgtestdb_conn.commit()

    # Return control to run test
    yield

    # Tear down
    with pgtestdb_conn.cursor() as cursor:
        cursor.execute("DROP SCHEMA IF EXISTS duplicate CASCADE", pgtestdb_conn)
    pgtestdb_conn.commit()