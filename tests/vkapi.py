

class Messages:

    def __init__(self, token):
        self.token = token

    def send(self, **kwargs) -> None:
        self.token = self.token


class FakeVkApi:

    def __init__(self, login=None, password=None, token=None,
                 auth_handler=None, captcha_handler=None,
                 config=None, config_filename='vk_config.v2.json',
                 api_version='5.92', app_id=6222115, scope=140492255,
                 client_secret=None, session=None):
        self.token = token
        self.api_version = api_version
        self.app_id = app_id
        self.scope = scope
        self.client_secret = client_secret
        self.session = session
        self.config = config
        self.config_filename = config_filename
        self.auth_handler = auth_handler
        self.captcha_handler = captcha_handler
        self.login = login
        self.password = password

        self.messages = Messages("")
