# -*- coding: utf-8 -*-

from odoo import models, exceptions, _
import tempfile, base64, zipfile, tarfile, mimetypes, logging
_logger = logging.getLogger(__name__)

PREFIX = 'utilities-import-'

class UtilitiesFileMixin(models.AbstractModel):
    _name = "utilities.file.mixin"
    _description = "Utilities File Management"

    def _uncompress(self, filename, content_b64):
        """ Return unarchived file content if archived. Supports bzip and gzip.
            If compressed, the archive must contain only 1 file

            :return: filename, content, mimetype
        """

        def __get_first(archive_members):
            if len(archive_members) != 1:
                raise exceptions.ValidationError(
                    _('This archive should contain 1 file (only).')
                )
            _logger.info(f'[_uncompress] __get_first, returning: {archive_members[0]}')
            return archive_members[0]
        
        with tempfile.NamedTemporaryFile('w+b', prefix=PREFIX + 'unzip-', suffix='.archive') as tmp:
            _logger.info(f'[_uncompress] tmp.name: {tmp.name}')
            tmp.write(base64.b64decode(content_b64))
            tmp.seek(0)

            # tarfile
            if tarfile.is_tarfile(tmp.name):
                _logger.info(f'[_uncompress] is_tarfile')
                with tarfile.open(tmp.name, "r:gz") as tar_archive:
                    filename = __get_first(tar_archive.getmembers())
                    content = tar_archive.extractfile(filename).read()
            
            # zip
            elif zipfile.is_zipfile(tmp.name):
                _logger.info(f'[_uncompress] is_zipfile')
                with zipfile.ZipFile(tmp.name) as zip_archive:
                    filename = __get_first(zip_archive.namelist())
                    content = zip_archive.read(filename)
            
            else:
                content = tmp.read()

            # not archived?
            _logger.info(f'[_uncompress] not archived, returning content')
            return filename, content, mimetypes.guess_type(filename)[0]

