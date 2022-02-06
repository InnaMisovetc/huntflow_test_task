import os
from typing import List, Dict

import magic
import requests

from app.candidate import Candidate
from app.schemas import AddCandidateSchema, AddCandidateToVacancySchema


class HuntFlowApi:
    def __init__(self, token: str, file_path: str) -> None:
        self.url = 'https://dev-100-api.huntflow.dev'
        self.headers = {'Authorization': f'Bearer {token}'}
        self.session = requests.Session()
        self.account_id = self.choose_account_id()
        self.file_path = file_path
        self.vacancies = self._get_vacancies()
        self.statuses = self._get_statuses()

    def get_accounts(self) -> List:
        """ Get list of available accounts for the provided token """

        url = f'{self.url}/accounts'
        r = self.session.get(url, headers=self.headers)
        accounts = r.json()['items']
        return accounts

    def choose_account_id(self) -> int:
        """ Choose account from the list of available accounts. Returns id of a chosen account """

        accounts = self.get_accounts()

        if not accounts:
            raise RuntimeError('No accounts have been found for this token')
        elif len(accounts) == 1:
            return accounts[0]['id']
        else:
            print('Choose the account to which you want to add candidates from the following options:')
            for number, account in enumerate(accounts, start=1):
                print(f'#{number}:', account['id'], account['name'])
            while True:
                index = input('Input index of the account: ')
                try:
                    index = int(index)
                    if index < 1 or index > len(accounts):
                        raise ValueError()
                except ValueError:
                    print('Invalid input. Input proper index')
                    continue
                return accounts[index - 1]['id']

    def _get_vacancies_on_page(self, url: str, vacancies_list: List, page: int = 1) -> int:
        """ Adds vacancies on a particular page to vacancies_list. Returns number of total pages """

        page = self.session.get(url, headers=self.headers, params={'opened': True, 'count': 30, 'page': page}).json()
        vacancies_list.extend(page['items'])
        return page['total']

    def _get_vacancies(self) -> List:
        """ Returns list of all open vacancies """

        url = f'{self.url}/account/{self.account_id}/vacancies'
        vacancies = []
        total = self._get_vacancies_on_page(url, vacancies)
        for page in range(2, total + 1):
            self._get_vacancies_on_page(url, vacancies, page)
        return vacancies

    def _get_statuses(self) -> List:
        """ Returns list of recruitment stages for the company """

        url = f'{self.url}/account/{self.account_id}/vacancy/statuses'
        response = self.session.get(url, headers=self.headers).json()
        return response['items']

    def upload_resume(self, file_path: str) -> Dict:
        """ Uploads file to the server. Returns parsed data of the resume"""

        url = f'{self.url}/account/{self.account_id}/upload'
        file_name = os.path.split(file_path)[-1]
        mime = magic.Magic(mime=True)
        files = {"file": (file_name, open(file_path, "rb"), mime.from_file(file_path))}
        headers = {**self.headers, "X-File-Parse": "true"}
        response = self.session.post(url=url, files=files, headers=headers)
        return response.json()

    def add_candidate(self, candidate: Candidate) -> Dict:
        """ Adds candidate data to the database """

        url = f'{self.url}/account/{self.account_id}/applicants'
        response = self.session.post(url=url, data=AddCandidateSchema().dumps(candidate), headers=self.headers)
        return response.json()

    def add_candidate_to_vacancy(self, candidate: Candidate) -> Dict:
        """ Adds candidate to the vacancy """

        url = f'{self.url}/account/{self.account_id}/applicants/{candidate.applicant_id}/vacancy'
        response = self.session.post(url=url, data=AddCandidateToVacancySchema().dumps(candidate), headers=self.headers)
        return response.json()
