from rest_framework.parsers import BaseParser


class CsvParser(BaseParser):

        HEADERS_DOWNLOAD = [
            {"field": 'status', "name": 'ステータス', 'default': 'Y'},
            {"field": 'employee_id', "name": '社員ID', 'default': '12345'},
            {"field": 'is_admin', "name": '管理者', 'default': 'N'},
            {"field": 'last_name', "name": '姓*', 'default': '高知' , 'required': True},
            {"field": 'first_name', "name": '名*', 'default': '太郎', 'required': True},
            {"field": 'last_furigana', "name": 'ふりがな（姓）', 'default': 'こうち'},
            {"field": 'first_furigana', "name": 'ふりがな（名）', 'default': 'たろう'},
            {"field": 'email', "name": 'メールアドレス*', 'default': 'kouchi@gmail.com', 'required': True},
            {"field": 'workshop_id', "name": 'ワークショップコード', 'default': 'WS001'},
            {"field": 'workshop_schedule', "name": 'ワークショップ日程', 'default': '1953/05/30', "format": "%Y/%m/%d"},
            {"field": 'assessment', "name": 'アセスメント', 'default': 'N'},
            {"field": 'email_magazine_delivery', "name": 'メルマガ配信', 'default': 'N'},
            {"field": 'last_login', "name": 'ログイン最終日時', "type": "date", "format": "%Y/%m/%d %H:%M:%S"},
            {"field": 'position', "name": '役職', 'default': 'マネージャー'},
            {"field": 'department', "name": '部署', 'default':'経営企画'},
            {"field": 'joined_month', "name": '入社月', 'default': 'Jul-90', "format": "%M-%y"},
            {"field": 'birthday', "name": '生年月日', 'default': '1953/05/30', "format": "%Y/%m/%d"},
            {"field": 'sex', "name": '性別', 'default': '1'},
            ]

        required_headers = [header for header in HEADERS_DOWNLOAD if "required" in header and header["required"] == True]
