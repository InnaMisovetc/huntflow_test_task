import argparse

from app.api import HuntFlowApi
from app.file_utils import FileUtils
from app.recovery import Recovery


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('token', type=str, help='Personal token for authorization')
    parser.add_argument('db_path', type=str, help='Path of the local database with candidates')
    args = parser.parse_args()
    return args.token, args.db_path


def main() -> None:
    token, db_path = parse_command_line()
    huntflow = HuntFlowApi(token=token,
                           file_path=db_path)
    file_utils = FileUtils(file_path=db_path)

    rec = Recovery(db_path)
    start_index = 0
    recovery_index = rec.try_load()
    if recovery_index is not None:
        start_index = recovery_index

    for candidate in file_utils.get_next_candidate(start_index, huntflow.vacancies, huntflow.statuses):
        path = file_utils.find_resume_file(candidate)

        upload_response = huntflow.upload_resume(path)
        candidate.process_upload_resume_response(upload_response)

        add_candidate_response = huntflow.add_candidate(candidate)
        candidate.process_add_candidate_response(add_candidate_response)

        huntflow.add_candidate_to_vacancy(candidate)
        print(f'Successfully added candidate {candidate.full_name} to the vacancy: {candidate.vacancy}')

    Recovery().reset()


if __name__ == '__main__':
    main()
