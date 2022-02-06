import os

from marshmallow import Schema, fields, post_load


class Recovery:
    FILE_NAME = 'recovery.json'
    RECOVERY_PROPOSAL = 'Processing of {file} was interrupted on candidate #{line}.' \
                        'You can [c]ontinue, [s]kip, or [r]estart. >  '
    INVALID_INPUT_ERROR = 'Input is not valid. Please, select from options: [c]ontinue, [s]kip, or [r]estart.'

    def __init__(self, file_path: str = "", line: int = 0) -> None:
        self.file_path = file_path
        self.line = line

    def try_load(self) -> int:
        """ Allows to choose whether to continue or skip the processing of the current candidate or restart the program.
         Returns line number in excel_file from which the processing should restart """

        if os.path.isfile(self.FILE_NAME):
            with open(self.FILE_NAME) as f:
                recovery = RecoverySchema().loads(f.read())
                if recovery.file_path == self.file_path:
                    response = input(
                        self.RECOVERY_PROPOSAL.format(file=recovery.file_path, line=recovery.line + 1)).lower()
                    if response == 'c' or response == 'continue':
                        return recovery.line
                    elif response == 's' or response == 'skip':
                        return recovery.line + 1
                    elif response == 'r' or response == 'restart':
                        return 0
                    else:
                        print(self.INVALID_INPUT_ERROR)
                        self.try_load()

    def save(self) -> None:
        """ Saves path of excel_file and line number of the candidate """

        with open(self.FILE_NAME, 'w') as f:
            f.write(RecoverySchema().dumps(self))

    def reset(self) -> None:
        """ Deletes file with the recovery data """

        os.remove(self.FILE_NAME)


class RecoverySchema(Schema):
    file_path = fields.Str()
    line = fields.Int()

    @post_load
    def make_recovery(self, data, **kwargs):
        return Recovery(**data)
