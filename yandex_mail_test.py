#!/usr/bin/env python

import unittest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from yandex_mail_wrapper import YandexMailWrapper


USERNAME = "test.test100500"
PASSWORD = "Passwo1!"


class TestSendMessage(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Remote(
            command_executor='http://192.168.99.100:32769/wd/hub',
            desired_capabilities=DesiredCapabilities.FIREFOX)
        self.driver.implicitly_wait(10)

        self.yandex_mail = YandexMailWrapper(self.driver)
        self.yandex_mail.login(USERNAME, PASSWORD)

    def test_receiver_subject_body_exists(self):
        self.yandex_mail.clear_list_of_sent_messages()

        self.yandex_mail.send_new_message(to="test.test100500@yandex.ru", subject="test", body="how you doin?")

        last_sent_message = self.yandex_mail.sent_messages.next()
        self.assertEqual(last_sent_message.to, "test.test100500@yandex.ru")
        self.assertEqual(last_sent_message.subject, "test")
        self.assertEqual(last_sent_message.body, "how you doin?")

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
