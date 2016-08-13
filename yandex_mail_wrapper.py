class YandexMailWrapper():
    def __init__(self, selenium_webdriver):
        self.driver = selenium_webdriver

    def login(self, username, password):
        login_page = LoginPage(self.driver)
        login_page.login(username, password)

    def send_new_message(self, to, subject, body):
        main_page = MainPage(self.driver)
        new_message_page = main_page.get_new_message_page()
        new_message_page.to = to
        new_message_page.subject = subject
        new_message_page.body = body
        new_message_page.send()

    def clear_list_of_sent_messages(self):
        main_page = MainPage(self.driver)
        sent_messages_page = main_page.get_sent_messages_page()
        sent_messages_page.clear_all()


    @property
    def sent_messages(self):
        main_page = MainPage(self.driver)
        sent_messages_page = main_page.get_sent_messages_page()
        return (message for message in sent_messages_page.sent_messages)


class BasePage():
    def __init__(self, selenium_webdriver):
        self.driver = selenium_webdriver


class LoginPage(BasePage):
    def login(self, username, password):
        pass


class MainPage(BasePage):
    def get_new_message_page(self):
        return NewMessagePage(self.driver)

    def get_sent_messages_page(self):
        return SentMessagesPage(self.driver)


class NewMessagePage(BasePage):
    @property
    def to(self):
        pass

    @to.setter
    def to(self):
        pass

    @property
    def subject(self):
        pass

    @subject.setter
    def subject(self):
        pass

    @property
    def body(self):
        pass

    @body.setter
    def body(self):
        pass

    def send(self):
        pass

class SentMessagesPage(BasePage):
    def clear_all(self):
        pass

    @property
    def sent_messages(self):
        pass
