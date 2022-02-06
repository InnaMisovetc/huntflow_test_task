import os
import unicodedata
from typing import List, Generator

import pandas as pd

from app.candidate import Candidate
from app.recovery import Recovery


class FileUtils:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def find_dir(self, candidate: Candidate) -> str:
        """ Finds directory where resume of the Candidate is located. Returns path of this directory """

        return os.path.join(os.path.dirname(self.file_path), candidate.vacancy)

    def find_resume_file(self, candidate: Candidate) -> str:
        """ Finds location of the candidate resume. Returns path of the resume """

        directory = self.find_dir(candidate)
        candidate_name = unicodedata.normalize('NFC', candidate.full_name.strip())
        for file in os.listdir(directory):
            file_name = unicodedata.normalize('NFC', os.path.splitext(file)[0])
            if candidate_name == file_name:
                return os.path.join(directory, file)

    def get_next_candidate(self, start_index: int, vacancies: List, statuses: List) -> Generator[Candidate, None, None]:
        """ Yields next candidate in the excel database """

        df = pd.read_excel(f'{self.file_path}', engine='openpyxl')
        for index in range(start_index, df.index.stop):
            Recovery(self.file_path, index).save()
            yield Candidate(df.loc[index], vacancies, statuses)
