import os
import re
from unittest.mock import MagicMock


def remove_duplicated_slash(filename):
    return re.sub(r'//*', '/', filename)


class MockBuiltinRead(MagicMock):
    def __init__(self, file_map):
        MagicMock.__init__(self, name=open, spec=open)
        self.file_map = file_map

        handle = MagicMock()
        handle.__enter__.return_value = handle
        handle.read.return_value = None

        def reset_choose_file(filename, *args, **kwargs):
            handle.read.return_value = self.file_map[remove_duplicated_slash(filename)]
            return handle

        self.side_effect = reset_choose_file


class MockOsPathExists(MagicMock):
    def __init__(self, file_map):
        MagicMock.__init__(self, name=os.path.exists, spec=os.path.exists)
        self.file_map = file_map

        def reset_choose_file(filename, *args, **kwargs):
            return remove_duplicated_slash(filename) in self.file_map.keys()

        self.side_effect = reset_choose_file
