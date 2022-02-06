from marshmallow import Schema, fields


class ExternalsSchema(Schema):
    data = fields.Nested(Schema.from_dict({
        "body": fields.Str()
    }))
    auth_type = fields.Str(default="NATIVE")
    files = fields.Nested(Schema.from_dict({
        "id": fields.Str()
    }), many=True)
    account_source = fields.Str()

    class Meta:
        ordered = True


class AddCandidateSchema(Schema):
    last_name = fields.Str()
    first_name = fields.Str()
    middle_name = fields.Str()
    phone = fields.Str()
    email = fields.Email()
    position = fields.Str()
    company = fields.Str()
    money = fields.Str()
    birthday_day = fields.Int()
    birthday_month = fields.Int()
    birthday_year = fields.Int()
    photo = fields.Int()
    externals = fields.Nested(ExternalsSchema, many=True)

    class Meta:
        ordered = True


class AddCandidateToVacancySchema(Schema):
    vacancy = fields.Int(attribute='vacancy_id')
    status = fields.Int(attribute='status_id')
    comment = fields.Str(default=None)

    class Meta:
        ordered = True
