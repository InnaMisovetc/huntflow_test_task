import argparse
import unicodedata

import magic
import requests
import pandas as pd
import os
import jsonpickle
import json


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('token')
    parser.add_argument('database_path')
    parser.parse_args()


class HuntFlowAPI:
    def __init__(self, token, file_path):
        self.url = 'https://dev-100-api.huntflow.dev'
        self.headers = {'Authorization': f'Bearer {token}'}
        self.session = requests.Session()
        self.account_id = self.get_account_id()
        self.file_path = file_path

    def get_account_id(self):
        url = f'{self.url}/accounts'
        r = self.session.get(url, headers=self.headers)
        return r.json()['items'][0]['id']

    def get_next_vacancies_page(self):
        url = os.path.join(self.url, 'account', str(self.account_id), 'vacancies')
        first_page = self.session.get(url, headers=self.headers, params={'opened': True}).json()
        yield first_page
        total = first_page['total']
        for page in range(2, total + 1):
            next_page = self.session.get(url, headers=self.headers, params={'page': page, 'opened': True}).json()
            yield next_page

    def upload_file(self, file_path):
        url = os.path.join(self.url, 'account', str(self.account_id), 'upload')

        file_name = os.path.split(file_path)[-1]
        mime = magic.Magic(mime=True)
        files = {"file": (file_name, open(file_path, "rb"), mime.from_file(file_path))}
        headers = {**self.headers, "X-File-Parse": "true"}
        response = requests.post(url=url, files=files, headers=headers)
        return response.json()

    def get_next_candidate(self):
        df = pd.read_excel(f'{self.file_path}')
        for index in range(0, df.index.stop):
            yield Candidate(df.loc[index])

    def find_dir(self, candidate):
        return candidate.vacancy

    def find_resume_file(self, candidate):
        directory = self.find_dir(candidate)
        candidate_name = unicodedata.normalize('NFC', candidate.full_name.strip())
        for file in os.listdir(directory):
            file_name = unicodedata.normalize('NFC', os.path.splitext(file)[0])
            if candidate_name == file_name:
                return os.path.join(directory, file)


class Candidate:
    def __init__(self, db_data):
        self.vacancy = db_data['Должность']
        self.full_name = db_data['ФИО']

        self.first_name = self.full_name.split(' ')[0]
        self.last_name = self.full_name.split(' ')[1]
        self.status = db_data['Статус']
        self.middle_name = None
        self.money = None
        self.phone = None
        self.email = None
        self.position = None
        self.birthday_day = None
        self.birthday_month = None
        self.birthday_year = None
        self.photo = None
        self.text = None
        self.resume = None

        if len(self.full_name.split(' ')) == 3:
            self.middle_name = self.full_name.split(' ')[2]
        if db_data["Ожидания по ЗП"]:
            self.money = db_data["Ожидания по ЗП"]

    def add_additional_data(self, data):
        fields = data['fields']
        if fields['phones']:
            self.phone = fields['phones'][0]
        self.email = fields['email']
        self.position = fields['position']
        birthdate = fields['birthdate']
        self.birthday_day = birthdate['day']
        self.birthday_month = birthdate['month']
        self.birthday_year = birthdate['year']
        self.photo = data['photo']['id']
        self.text = data['text']
        self.resume = data['id']


huntflow = HuntFlowAPI(token='71e89e8af02206575b3b4ae80bf35b6386fe3085af3d4085cbc7b43505084482', file_path=r'/Users/innamisovetc/dev/huntflow_test_task/Тестовая база.xlsx')

for candidate in huntflow.get_next_candidate():
    path = huntflow.find_resume_file(candidate)
    data = huntflow.upload_file(path)
    candidate.add_additional_data(data)
    obj = jsonpickle.encode(candidate, unpicklable=False)
    print(json.loads(obj))
    break

