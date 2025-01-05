# -*- coding: utf-8 -*-

from odoo import models, exceptions, _
import tempfile, base64, zipfile, tarfile, mimetypes, logging
_logger = logging.getLogger(__name__)

import sqlite3, subprocess # for MDB->sqlite

PREFIX = 'temp-db-'

class UtilitiesDatabaseMixin(models.AbstractModel):
    _name = "utilities.database.mixin"
    _description = "Utilities Database Management"


    #===== Open a database =====#
    def _open_external_database(self, filename, db_content, mimetype, encoding, db_models=[], db_user=None, db_password=None):
        """ Main method called from the client model
            :option models: if given, can be used to limit the tables/models to read
            :return: db_resource, record of `base.external.dbsource` *OR* tuple of SQLite (connection, cursor)
        """
        # [IMP][2024-11] Use OCA connectors, module `base_external_db_source` and affiliated
        with_oca_connector = False

        with tempfile.NamedTemporaryFile(mode='w+b', prefix=PREFIX, suffix='.db') as tmp:
            _logger.info(f'[_open_external_database] db_filename: {tmp.name}')
            tmp.write(db_content)
            tmp.seek(0)

            if with_oca_connector:
                db_resource = self._get_dbsource(
                    filename=tmp.name,
                    mimetype=mimetype,
                    encoding=encoding,
                    db_models=db_models,
                    db_user=db_user,
                    db_password=db_password,
                )
            else:
                connection, cursor = self._get_sqlite_resource(
                    filename=tmp.name,
                    mimetype=mimetype,
                    encoding=encoding,
                    db_models=db_models
                )
                db_resource = connection, cursor

        _logger.info(f'[_open_external_database] Ending well with connection, cursor: {connection}, {cursor}')
        
        return db_resource

    #===== Read models in a database =====#
    def _read_db(self, db_resource, request, cols_mapping={}, format_m2m=False):
        """ 
            :arg db_resource: record of `base.external.dbsource` *OR* tuple of SQLite (connection, cursor)
            :arg request: SQL request (str) to execute
            :option cols_mapping: dict with external db columns as key and Odoo column in vals
                                    usefull to prepare an Odoo `vals_list`
            :option format_m2m: to output return in shorten format, if possible

            :return:
                2 possible output format: 
                 - default: `vals_list` format (list of vals dict)
                 - shorten format: single dict of {val0_col1: val0_col2, ...}
                    o format_m2m=True
                    o request outputs only 2 columns
                    o in this case, `cols_mapping`
        """
        cols, rows = self._execute_db(db_resource, request)

        # shorten format {val0_col1: val0_col2, ...}
        if format_m2m and len(cols) == 2:
            return {row[0]: row[1] for row in rows}
        else: # default `vals_list` format
            return [{
                cols_mapping.get(col, col): row[x]
                for x, col in enumerate(cols)
            } for row in rows]

    def _execute_db(self, db_resource, request):
        try:
            # Sqlite (connection, cursor)
            if len(db_resource) == 2:
                _, cursor = db_resource
                cursor.execute(request)
                rows = cursor.fetchall()
                cols = [x[0] for x in cursor.description]
            
            # OCA connector
            else:
                # `db_resource` is a record of `base.external.dbsource`
                result = db_resource.execute(request, metadata=True)
                cols, rows = result['cols'], result['rows']
        except Exception as e:
            raise exceptions.UserError(
                _('Issue when reading external table. Request: %s') % request
            )
        
        return cols, rows
    
    def _close_db(self, db_resource):
        # Sqlite (connection, cursor)
        if len(db_resource) == 2:
            connection, _ = db_resource
            connection.close()
        # OCA connector
        else:
            db_resource.connection_close()
        
    #===== Import external data to Odoo =====#
    def _import_data(self, vals_list, existing_ids, primary_keys, sequence=True):
        """ Create or update Odoo records from external db `vals_list`
            
            :option primary_keys:
                Primary key fields. Saved in Odoo table, and allow matching
                 an Odoo record with its source in case of a new import
            :sequence: 
                if True, `sequence` field is added to `vals` when creating new Odoo
                 records, allowing to keep same order than in external db
            
            :return:
                Existing records + created ones
        """
        # Dict to reverse from primary_keys to existing record (if any)
        mapped_data = {
            tuple([rec[field] for field in primary_keys]): rec
            for rec in existing_ids
        }
        to_create = []
        for seq, vals in enumerate(vals_list):
            key = tuple([vals.get(field) for field in primary_keys])
            record = mapped_data.get(key)
            vals = vals | {'project_id': self.project_id.id} | ({'sequence': seq} if sequence else {})

            if record and record.id:
                record.write(vals)
            else:
                to_create.append(vals)
        
        return existing_ids | existing_ids.create(to_create)





    #===== Open database and return a resource to read in it: with OCA connector =====#
    def _get_dbsource(self, **kwargs):
        vals = self._get_dbsource_vals(**kwargs)
        _logger.info(f'[_get_dbsource] vals: {vals}')
        dbsource = self.env['base.external.dbsource'].create(vals)
        dbsource.connection_test()
        dbsource.connection_open()
        return dbsource

    def _get_dbsource_vals(self, filename='', mimetype='', encoding='', db_models=[], db_user=None, db_password=None):
        """ Can be inherited to add more database format support """

        vals = {
            'name': 'MDB-' + filename,
            'conn_string': f"Server=localhost;Database={filename}{ f';User Id={db_user}' if db_user else '' }",
        } | ({'password': db_password} if db_password else {})

        # MsAccess
        specific_vals = {}
        if mimetype in ['application/x-msaccess', 'application/msaccess']:
            # ODBC
            vals.update({
                'conn_string': f"DRIVER={{FreeTDS}};SERVER=localhost;Database={filename}{ f';UID={db_user}' if db_user else ''}",
                'connector': 'mssql'
            })

            # MSSQL
            # vals.update({
            #     'conn_string': f'mssql+pymssql://username:{db_user}@localhost/{filename}?charset={encoding}',
            #     'connector': 'mssql'
            # })
        # MsAccess
        elif mimetype in ['application/x-sqlite3']:
            vals.update({'connector': 'sqlite'})
        else:
            raise exceptions.ValidationError(f'[_get_dbsource_vals] Database type is not supported: {mimetype}')
        
        return vals

    #===== Open database and return a resource to read in it: mdb->sqlite =====#
    def _get_sqlite_resource(self, filename, mimetype, encoding, db_models=[]):
        if mimetype in ['application/x-msaccess', 'application/msaccess']:
            _logger.info(f'[_get_sqlite_resource] Converting .MDB to Sqlite db_filename: {filename}')
            connection, cursor = self._mdb_to_sqlite(filename, encoding=encoding, db_models=db_models)
        else:
            try:
                connection = sqlite3.connect(filename)
                cursor = connection.cursor()
            except Exception as e:
                raise exceptions.ValidationError(
                    _('Cannot initiate sqlite3 database. Details : %s', e)
                )
            _logger.info(f'[_get_sqlite_resource] Ending well with connection, cursor: {connection}, {cursor}')
            
        return connection, cursor

    def _mdb_to_sqlite(self, mdb_filename, encoding='utf-8', db_models=[]):
        """ See https://gist.github.com/jsundram/f362c5a62e0dc9cb1aab9c815d9e5b5c """

        def __shellexec(cmd):
            """runs the command, returns the decoded output as a single string"""
            return subprocess.check_output(cmd).decode(encoding, 'ignore').replace('\x00', '')

        # list tables names
        def __get_table_list(mdb_filename):
            delimiter = ", "
            output = __shellexec(["mdb-tables", "-d", delimiter, mdb_filename])
            tables = output.split(delimiter)
            return [stripped for t in tables if (stripped := t.strip()) != ""]
        db_models = db_models or __get_table_list(mdb_filename)

        # initiating a new sqlite database (empty yet)
        _logger.info(f'[_mdb_to_sqlite] converting mdb to sqlite3 (tempfile: :memory:)')
        connection = sqlite3.connect(':memory:')
        cursor = connection.cursor()
    
        # populate sqlite database from .MDB data
        create = "mdb-schema --indexes --relations --default-values --not-null".split(" ")
        for table in db_models:
            _logger.info(f'[mdb_to_sqlite] creating table {table})')
            table_create = __shellexec(create + [mdb_filename, "-T", table, "sqlite"])
            cursor.execute(table_create)

            sql = __shellexec(["mdb-export", "-I", "sqlite", "-S", "1", mdb_filename, table])
            for i, insert in enumerate(sql.split(";\n")):
                try:
                    cursor.execute(insert)
                except Exception as e:
                    raise exceptions.ValidationError(_('Error when populating SQLITE database from MDB: \n %s', e))
            _logger.info(f'[mdb_to_sqlite] table {table}: {i} records inserted')
            connection.commit()
        
        _logger.info(f'[mdb_to_sqlite] ending conversion of MDB to SQLITE')
        return connection, cursor
