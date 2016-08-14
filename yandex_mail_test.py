#!/usr/bin/env python

import unittest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from yandex_mail_wrapper import YandexMailWrapper, MessageSendingFailed


USERNAME = "test.test100500"
PASSWORD = "Passwo1!"


class FailedLogin(Exception):
    pass


class TestSendMessage(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Remote(
            command_executor='http://192.168.99.100:32769/wd/hub',
            desired_capabilities=DesiredCapabilities.FIREFOX)
        self.driver.implicitly_wait(10)

        self.yandex_mail = YandexMailWrapper(self.driver)
        login_result = self.yandex_mail.login(USERNAME, PASSWORD)
        if not login_result:
            self.driver.quit()
            raise FailedLogin("used username: {0}, password: {1}".format(USERNAME, PASSWORD))

    def test_receiver_subject_body_exists(self):
        """to=1, subj=1, body=1"""
        self.yandex_mail.clear_list_of_sent_messages()

        self.yandex_mail.send_new_message(to="test.test100500@yandex.ru", subject="test", body="how you doin?")

        last_sent_message = next(self.yandex_mail.sent_messages)
        self.assertEqual(last_sent_message["to"], ("test.test100500@yandex.ru", ))
        self.assertEqual(last_sent_message["subject"], "test")
        self.assertEqual(last_sent_message["body_first_line"], "how you doin?")

    def test_no_body(self):
        """to=1, subj=1, body=0"""
        self.yandex_mail.clear_list_of_sent_messages()

        self.yandex_mail.send_new_message(to="test.test100500@yandex.ru", subject="subj", body="")

        last_sent_message = next(self.yandex_mail.sent_messages)
        self.assertEqual(last_sent_message["to"], ("test.test100500@yandex.ru", ))
        self.assertEqual(last_sent_message["subject"], "subj")
        assert("body_first_line" not in last_sent_message)

    @unittest.expectedFailure
    def test_no_subject(self):
        """to=1, subj=0, body=1"""
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="test.test100500@yandex.ru", subject="", body="body")

    @unittest.expectedFailure
    def test_no_subject_no_body(self):
        """to=1, subj=0, body=0"""
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="test.test100500@yandex.ru", subject="", body="")

    def test_no_receiver(self):
        """to=0, subj=1, body=1"""
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="", subject="subject", body="body")

    def test_no_receiver_no_body(self):
        """to=0, subj=1, body=0"""
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="", subject="subject", body="")

    def test_no_receiver_no_subject(self):
        """to=0, subj=0, body=1"""
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="", subject="", body="body")

    def test_no_receiver_no_subject_no_body(self):
        """to=0, subj=0, body=0"""
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="", subject="", body="")


    def test_two_receivers(self):
        self.yandex_mail.clear_list_of_sent_messages()

        self.yandex_mail.send_new_message(to="test.test100500@yandex.ru, al.ol.chistyakov@gmail.com", subject="test", body="how you doin?")

        last_sent_message = next(self.yandex_mail.sent_messages)
        self.assertEqual(last_sent_message["to"], ("test.test100500@yandex.ru", "al.ol.chistyakov@gmail.com"))
        self.assertEqual(last_sent_message["subject"], "test")
        self.assertEqual(last_sent_message["body_first_line"], "how you doin?")

    #There are a lot possible tests for invalid mails
    #it's better to test it on unit level
    def test_not_valid_mail_no_at(self):
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="test.test100500", subject="subject", body="body")

    def test_not_valid_mail_no_domen(self):
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="test.test100500@", subject="subject", body="body")

    def test_not_valid_mail_no_mailname(self):
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="@gmail.com", subject="subject", body="body")

    def test_not_valid_mail_no_high_level_domain(self):
        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to="test.test100500@gmail", subject="subject", body="body")

    def test_valid_mail_russian_mailname(self):
        self.yandex_mail.clear_list_of_sent_messages()

        self.yandex_mail.send_new_message(to="тест@почта.рф", subject="subject", body="body")
        last_sent_message = next(self.yandex_mail.sent_messages)
        self.assertEqual(last_sent_message["to"], ("тест@почта.рф", ))
        self.assertEqual(last_sent_message["subject"], "subject")
        self.assertEqual(last_sent_message["body_first_line"], "body")

    def test_max_mail_length_is_254_equal_to_boundary(self):
        mailbox = "a" * (254 - len("@gmail.com"))
        mailbox = "".join((mailbox, "@gmail.com"))
        assert len(mailbox) == 254
        self.yandex_mail.clear_list_of_sent_messages()

        self.yandex_mail.send_new_message(to=mailbox, subject="subject", body="body")

        last_sent_message = next(self.yandex_mail.sent_messages)

        self.assertEqual(last_sent_message["to"], (mailbox, ))
        self.assertEqual(last_sent_message["subject"], "subject")
        self.assertEqual(last_sent_message["body_first_line"], "body")

    @unittest.expectedFailure
    def test_max_mail_length_is_254_more_then_boundary(self):
        mailbox = "a" * (255 - len("@gmail.com"))
        mailbox = "".join((mailbox, "@gmail.com"))
        assert len(mailbox) == 255

        with self.assertRaises(MessageSendingFailed):
            self.yandex_mail.send_new_message(to=mailbox, subject="subject", body="body")

    #TODO: add tests for CC and BCC
    #TODO: add tests for boundary values of maximum number of receivers, maximum length of subject and body
    #TODO: add tests with attachments
    #TODO: add tests with markdown in body
    #TODO: add tests for hotkeys


    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
