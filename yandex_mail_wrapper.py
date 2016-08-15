# -*- coding: utf-8 -*-

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


class YandexMailWrapper():
    def __init__(self, selenium_webdriver):
        self.driver = selenium_webdriver

    def login(self, username, password):
        login_page = LoginPage(self.driver)
        login_page.login(username, password)
        main_page = MainPage(self.driver)
        main_page.wait_until_page_is_loaded()
        return "Входящие" in self.driver.title

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
        return sent_messages_page.sent_messages


class BasePage():
    MAINPAGE_URL = "https://mail.yandex.ru"
    def __init__(self, selenium_webdriver):
        self.driver = selenium_webdriver


class LoginPage(BasePage):
    def login(self, username, password):
        self.driver.get(self.MAINPAGE_URL)
        username_textbox = self.driver.find_element_by_name("login")
        username_textbox.send_keys(username)
        password_textbox = self.driver.find_element_by_name("passwd")
        password_textbox.send_keys(password)
        login_button = self.driver.find_element_by_xpath("//button[@type='submit']")
        login_button.click()


class MainPage(BasePage):
    def __init__(self, *args):
        super().__init__(*args)
        self.open_main_page()

    def open_main_page(self):
        self.driver.get(self.MAINPAGE_URL)

    def get_new_message_page(self):
        new_mail = self.driver.find_element_by_xpath("//a[@title='Написать (w, c)']")
        new_mail.click()
        return NewMessagePage(self.driver)

    def get_sent_messages_page(self):
        self.refresh_messages()
        sent_messages = self.driver.find_element_by_xpath("//a[@title='Отправленные']")
        sent_messages.click()
        return SentMessagesPage(self.driver)

    def refresh_messages(self):
        refresh_button = self.driver.find_element_by_class_name("js-toolbar-item-check-mail")
        refresh_button.click()
        self.wait_until_page_is_loaded()

    def wait_until_page_is_loaded(self):
        def page_is_loading(driver):
            loading_indicator_elem = driver.find_element_by_class_name("b-stamp_default")
            return "b-stamp_loading" in loading_indicator_elem.get_attribute("class").split()
        WebDriverWait(self.driver, 10).until_not(page_is_loading)



class MessageSendingFailed(Exception):
    pass


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
        try:
            WebDriverWait(self.driver, 10).until(
                lambda driver: "Письмо успешно отправлено." in driver.page_source)
        except TimeoutException:
            raise MessageSendingFailed

    def _unfocus(self):
        self.driver.find_element_by_class_name("b-compose").click()


class SentMessagesPage(BasePage):
    def clear_all(self):
        self.select_all()
        self.click_remove()

    def select_all(self):
        checkbox_select_all = self.driver.find_element_by_xpath("//label[text()='Отправленные']")
        checkbox_select_all.click()
        #link_select_all_in_folder = self.driver.find_element_by_link_text("Выбрать все письма в этой папке")
        #link_select_all_in_folder.click()

    def click_remove(self):
        remove_button = self.driver.find_element_by_xpath("//a[@title='Удалить (Delete)']")
        remove_button.click()

    @property
    def sent_messages(self):
        try:
            messages_box = self.driver.find_element_by_xpath("(//div[@class='block-messages-wrap'])[2]/div[@class='b-messages']")
        except NoSuchElementException:
            raise StopIteration
        messages = messages_box.find_elements_by_xpath("./*")
        for m in messages:
            to = tuple(el.get_attribute('title') for el in m.find_elements_by_class_name("b-messages__from__text"))
            subj = m.find_element_by_class_name("b-messages__subject").text
            try:
                body_first_line = m.find_element_by_class_name("b-messages__firstline").text
            except NoSuchElementException:
                yield ({"to": to, "subject": subj})
            yield ({"to": to, "subject": subj, "body_first_line": body_first_line})


