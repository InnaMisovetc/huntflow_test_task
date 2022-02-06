from typing import List, Dict


class HuntFlowAPIUtils:

    @staticmethod
    def get_vacancy_id_by_name(vacancy_name: str, vacancies: List) -> int:
        """ Finds vacancy id by its name """

        for vacancy in vacancies:
            if vacancy['position'] == vacancy_name:
                return vacancy['id']

    @staticmethod
    def get_status_by_name(status_name: str, statuses: List) -> Dict:
        """ Finds status by its name """

        for status in statuses:
            if status['name'] == status_name:
                return status
