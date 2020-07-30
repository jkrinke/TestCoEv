import logging
from datetime import datetime

from pydriller import RepositoryMining
from pydriller.domain.commit import Modification
from commits2sql.database import TableHandlerFactory, Recorder
from modification import Extractor


class Main(object):

    def __init__(
            self, tmp_data_dir: str, repos_path: str,
    ):
        repos_name = repos_path.rpartition('/')[-1]
        self.__recorder = Recorder(TableHandlerFactory(tmp_data_dir, repos_name))
        self.__repos_path = repos_path

    def mining(self, start_date: datetime = None, end_date: datetime = None):
        for commit in RepositoryMining(self.__repos_path, since=start_date, to=end_date).traverse_commits():
            if not self.__recorder.is_record_before(commit.hash):
                for modification in commit.modifications: self.__handle_modification(modification, commit.hash)
                self.__recorder.record_git_commit(commit.hash, commit.author_date)


    def __handle_modification(self, modification: Modification, commit_hash: str):
        file = Extractor(modification).get_changed_file()
        if file.is_renamed(): self.__recorder.record_file_relocate(file.path_before, file.path_current)
        path = file.path_current if file.path_current is not None else file.path_before
        for f_class in file.classes:
            if f_class.is_renamed():self.__recorder.record_rename_class(path, f_class.name_before, f_class.name_current)
            class_name = f_class.name_current if f_class.name_current is not None else f_class.name_before
            for method in f_class.methods:
                if method.is_renamed():
                    before, current = method.method_before, method.method_current
                    old_name, cur_name = before.long_name, current.long_name
                    before_id = self.__recorder.get_method_id(old_name, class_name, path)
                    try: self.__recorder.record_rename_method(before_id, cur_name, commit_hash)
                    except: logging.warning(f'error for renaming method_{before_id}: from {old_name} to ({cur_name})')
                elif method.is_new():
                    new_id = self.__recorder.get_method_id(method.method_current.long_name, class_name, path)
                    self.__recorder.record_add_method(new_id, commit_hash)
                elif method.is_deleted():
                    before_id = self.__recorder.get_method_id(method.method_before.long_name, class_name, path)
                    self.__recorder.record_remove_method(before_id, commit_hash)
                elif method.is_modified():
                    method_id = self.__recorder.get_method_id(method.method_before.long_name, class_name, path)
                    self.__recorder.record_modify_method(method_id, commit_hash)