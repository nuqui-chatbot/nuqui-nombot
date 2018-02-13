import threading
import time
import datetime

import schedule
import random

from nombot import telegram
from nombot import database
from nombot import plotter
from nombot import quiz
from nombot.strings import MESSAGES


class NombotScheduler():
    def __init__(self):
        self.count = 0

    def test_job(self):
        schedule.every(10).seconds.do(lambda: telegram.send_message("Scheduler_test", 123561529))

    def suggestion_jobs(self):
        self.quiz_time()
        schedule.every().day.at("11:00").do(self.remember_breakfast_suggestion)
        schedule.every().day.at("14:00").do(self.remember_lunch_suggestion)
        schedule.every().day.at("17:00").do(self.remember_snacks_suggestions)
        schedule.every().day.at("20:00").do(self.remember_dinner_suggestion)
        schedule.every().day.at("15:30").do(self.suggestions)

    def monitoring_jobs(self):
        self.quiz_time()
        schedule.every().day.at("9:00").do(self.send_weight_history)
        schedule.every().day.at("21:00").do(self.send_daily_calories)

    def comparison_jobs(self):
        self.quiz_time()
        schedule.every().day.at("20:30").do(self.compare_to_other)

    def competition_jobs(self):
        self.quiz_time()
        schedule.every().day.at("20:45").do(self.compare_to_other)


    def basic_quiz_jobs(self):
        schedule.every().day.at("10:00").do(self.quiz_time)
        schedule.every().day.at("13:00").do(self.quiz_time)
        schedule.every().day.at("19:00").do(self.quiz_time)


    def quiz_time(self):
        users = database.get_all_user()
        for user_id in users:
            quiz.handle_quiz_request(user_id)

    def remember_lunch_suggestion(self):
        users = database.get_suggestion_users()
        messages = MESSAGES.get("remember_lunch")
        for user in users:
            telegram.send_message(random.choice(messages), user)

    def remember_breakfast_suggestion(self):
        users = database.get_suggestion_users()
        messages = MESSAGES.get("remember_breakfast")
        for user in users:
            telegram.send_message(random.choice(messages), user)

    def remember_dinner_suggestion(self):
        users = database.get_suggestion_users()
        messages = MESSAGES.get("remember_dinner")
        for user in users:
            telegram.send_message(random.choice(messages), user)

    def remember_snacks_suggestions(self):
        users = database.get_suggestion_users()
        messages = MESSAGES.get("remember_snacks")
        for user in users:
            telegram.send_message(random.choice(messages), user)

    def suggestions(self):
        users = database.get_suggestion_users()
        messages = MESSAGES.get("suggestions")
        for user in users:
            telegram.send_message(random.choice(messages), user)

    def send_daily_calories(self):
        users = database.get_self_monitoring_users()
        for user in users:
            plotter.plot_daily_calories(self, user)
            file = {'photo': open('nombot/data/' + user + '.png', 'rb')}
            telegram.send_photo(file, user)

    def send_weight_history(self):
        users = database.get_self_monitoring_users()
        for user in users:
            try:
                plotter.plot_weight_history(self, user)
                file = {'photo': open('nombot/data/' + str(user) + '.png', 'rb')}
                telegram.send_photo(file, user)
            except FileNotFoundError:
                pass

    def compare_to_other(self):
        users = database.get_all_user()
        for user in users:
            random_user = database.get_random_user(user)
            random_user_name = random_user.name
            now = datetime.datetime.now()
            dateformat = '%Y-%m-%d'
            daily_calories = database.get_calories_day(random_user, now.strftime(dateformat))
            telegram.send_message(
                "Interested in the results of others? " + random_user_name + " had " + daily_calories + "kcal today so far.",
                user)

    def competition_messages(self):
        users = database.get_competition_users()
        messages = MESSAGES.get("competition")
        for user in users:
            telegram.send_message(random.choice(messages), user)

    def job(self):
        print("I'm working...")

    def run_continuously(self):
        pass


class ScheduleThread(threading.Thread):
    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
