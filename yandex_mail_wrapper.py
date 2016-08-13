# -*- coding: utf-8 -*-

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
    LOGIN_URL = "https://mail.yandex.ru"
    def login(self, username, password):
        self.driver.get(self.LOGIN_URL)
        username_textbox = self.driver.find_element_by_name("login")
        username_textbox.send_keys(username)
        password_textbox = self.driver.find_element_by_name("passwd")
        password_textbox.send_keys(password)
        login_button = self.driver.find_element_by_xpath("//button[@type='submit']")
        login_button.click()


class MainPage(BasePage):
    MAINPAGE_URL = "https://mail.yandex.ru"
    def open_main_page(self):
        self.driver.get(self.MAINPAGE_URL)

    def get_new_message_page(self):
        new_mail = self.driver.find_element_by_xpath("//a[@title='Написать (w, c)']")
        new_mail.click()
        return NewMessagePage(self.driver)

    def get_sent_messages_page(self):
        return SentMessagesPage(self.driver)


class NewMessagePage(BasePage):
    def __init__(self, *args):
        super().__init__(*args)
        self.to_textbox = self.driver.find_element_by_class_name("b-mail-input_yabbles__focus")
        self.subject_textbox = self.driver.find_element_by_name("subj")
        self.body_frame = self.driver.find_element_by_id('compose-send_ifr')


    @property
    def to(self):
        return self.to_textbox.get_attribute('value')

    @to.setter
    def to(self, value):
        self._unfocus()
        self.to_textbox.send_keys(value)

    @property
    def subject(self):
        return self.subject_textbox.get_attribute('value')

    @subject.setter
    def subject(self, value):
        self.subject_textbox.send_keys(value)

    @property
    def body(self):
        self.driver.switch_to.frame(self.body_frame)
        body_input = self.driver.find_element_by_id("tinymce")
        value = body_input.get_attribute('value')
        self.driver.switch_to.default_content()
        return value

    @body.setter
    def body(self, value):
        self.driver.switch_to.frame(self.body_frame)
        body_input = self.driver.find_element_by_id("tinymce")
        body_input.send_keys(value)
        self.driver.switch_to.default_content()

    def send(self):
        send_button = self.driver.find_element_by_xpath("//button[@title='Отправить письмо (Ctrl + Enter)']")
        send_button.click()

    def _unfocus(self):
        self.driver.find_element_by_class_name("b-compose").click()


class SentMessagesPage(BasePage):
    def clear_all(self):
        pass

    @property
    def sent_messages(self):
        pass
