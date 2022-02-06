from typing import List, Dict

from pandas.core.series import Series

from app.api_utils import HuntFlowAPIUtils


class Candidate:
    def __init__(self, db_data: Series, vacancies: List, statuses: List) -> None:
        self.vacancy = db_data['Должность'].strip()
        self.full_name = db_data['ФИО'].strip()

        # Name
        self.last_name = self.full_name.split(' ')[1]
        self.first_name = self.full_name.split(' ')[0]
        if len(self.full_name.split(' ')) == 3:
            self.middle_name = self.full_name.split(' ')[2]

        self.phone = None
        self.email = None
        self.position = None
        self.company = None

        # Money expectations
        if db_data["Ожидания по ЗП"]:
            self.money = db_data["Ожидания по ЗП"]
        else:
            self.money = None

        # Birthday
        self.birthday_day = None
        self.birthday_month = None
        self.birthday_year = None

        # Photo
        self.photo = None

        # Externals
        self.externals = [{}]
        self.externals[0]["data"] = {"body": None}
        self.externals[0]["files"] = {"id": None}
        self.externals[0]["account_source"] = None

        # Status
        status = db_data['Статус']
        self.status = HuntFlowAPIUtils().get_status_by_name(status, statuses)
        self.status_id = self.status['id']

        # Comment
        comment = db_data['Комментарий']
        self.comment = comment

        # Vacancy id
        self.vacancy_id = HuntFlowAPIUtils().get_vacancy_id_by_name(self.vacancy, vacancies)

        # Candidate id
        self.applicant_id = None

    def process_upload_resume_response(self, response: Dict) -> None:
        """ Process parsed resume data """

        response_fields = response['fields']
        self.position = response_fields['position']
        self.email = response_fields['email']

        # Phones
        if len(response_fields['phones']) > 0:
            self.phone = response_fields['phones'][0]

        # Birthdate
        response_birthdate = response_fields['birthdate']
        if response_birthdate:
            self.birthday_day = response_birthdate['day']
            self.birthday_month = response_birthdate['month']
            self.birthday_year = response_birthdate['year']

        # Photo
        response_photo = response['photo']
        if response_photo:
            self.photo = response_photo['id']

        # Resume
        self.externals[0]['data'] = {'body': response['text']}
        self.externals[0]['files'] = [{'id': response['id']}]

    def process_add_candidate_response(self, response: Dict) -> None:
        """ Retrieves applicant_id from response and assigns it to the candidate object  """

        self.applicant_id = response['id']
