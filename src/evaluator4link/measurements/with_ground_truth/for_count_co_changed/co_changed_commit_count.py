from typing import Dict, Tuple, List

from evaluator4link.measurements import StrategyWithGroundTruthMeasurement
from evaluator4link.measurements.utils import GroundTruthMethodName


class CoChangedCommitCountMeasurement(StrategyWithGroundTruthMeasurement):

    @property
    def __select_co_changed_commits_sql_stmt(self) -> str: return '''
        WITH test_commits AS (
            SELECT target_method_id AS test_id, commit_hash FROM changes
            WHERE target_method_id = :test_method_id
        ), tested_commits AS (
            SELECT target_method_id AS tested_id, commit_hash FROM changes
            WHERE target_method_id = :tested_method_id
        )
        SELECT test_commits.commit_hash FROM (
            test_commits INNER JOIN tested_commits
            ON test_commits.commit_hash = tested_commits.commit_hash
        )
    '''

    @property
    def __select_co_changed_methods_with_commits_sql_stmt(self) -> str: return '''
        WITH co_changed_ids AS (
            SELECT test_method_id, tested_method_id FROM co_changed_for_commits
            WHERE test_method_id = :test_method_id
        ), test_commits AS (
            SELECT target_method_id AS test_id, commit_hash FROM changes
            WHERE target_method_id = :test_method_id
        ), tested_commits AS (
            SELECT target_method_id AS tested_id, commit_hash FROM (
                changes INNER JOIN co_changed_ids
                ON target_method_id = co_changed_ids.tested_method_id
            )
        )
        SELECT tested_id, test_commits.commit_hash FROM (
            test_commits INNER JOIN tested_commits
            ON test_commits.commit_hash = tested_commits.commit_hash
        )
    '''



    def __init__(self, path_to_db: str, path_to_csv: str):
        self.__commits_ground_truth_coordinates: Dict[int, int] = dict() # commit, number of ground truths
        self.__commits_co_changed_coordinates: Dict[int, int] = dict()
        self.__commit_x_mapping: Dict[str, int] = dict()
        super().__init__(path_to_db, path_to_csv, 'co_changed_for_commits')

    def _measure(self) -> None:
        for row in self._ground_truth_pandas.itertuples():
            test, tested = GroundTruthMethodName(row[1]), GroundTruthMethodName(row[2])
            test_id, tested_id = self.get_method_id_by_(test), self.get_method_id_by_(tested)
            for commit in self.__get_co_changed_commits_for(test_id, tested_id):
                cur_num = self.__commits_ground_truth_coordinates.setdefault(commit, 0)
                self.__commits_ground_truth_coordinates[commit] = cur_num + 1
        for
        return None

    def __get_co_changed_commits_for(self, test_id: int, tested_id: int) -> List[int]:


    def __from_commits_to_x(self, hash_value: str) -> int:
        if hash_value not in self.__commit_x_mapping:
            self.__commit_x_mapping[hash_value] = len(self.__commit_x_mapping) + 1
        return self.__commit_x_mapping[hash_value]




