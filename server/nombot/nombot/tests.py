import datetime

from django.test import TestCase

from nombot.chatbot import AIMLMessageHandler, ClassificationMessageHandler, ChatBot
from nombot.classification import Classifier
from nombot.models import User, Meal, WeightEntry, MealEntry
from nombot import chatbot
from nombot import database

USER_ID = 12
USER_HEIGHT = 178
FIRST_NAME = "Franz"
LAST_NAME = "Xare"
GAME_TYPE_COMPETITION = chatbot.COMPETITION
GENDER_MALE = "M"


def set_up_database():
    user = User()
    user.first_name = FIRST_NAME
    user.gametype = GAME_TYPE_COMPETITION
    user.gender = GENDER_MALE
    user.height = USER_HEIGHT
    user.user_id = USER_ID
    user.save()

    save_meals(["Wurstbrot", "rice pudding", "butter pretzel", "cookie", "apple pie",
                "sausage salad", "lasagna"])


def save_meals(meal_names):
    for meal_name in meal_names:
        save_meal(meal_name)


def save_meal(name):
    meal = Meal()
    meal.name = name
    meal.calories = 200
    meal.carbs = 20
    meal.fat = 30
    meal.protein = 40
    meal.save()
    return meal


class DatabaseTestCase(TestCase):
    def setUp(self):
        self.date = datetime.datetime.now()
        self.user = database.save_user(user_id=USER_ID, first_name=FIRST_NAME, last_name=LAST_NAME)
        database.save_height(USER_ID, self.date, USER_HEIGHT)

        self.user.gender = GENDER_MALE
        self.user.gametype = GAME_TYPE_COMPETITION
        self.user.height = USER_HEIGHT
        self.user.save()

        self.meal = database.create_meal(name="lasagna", calories=310, fat=12, carbs=35, protein=16)
        date = datetime.datetime.now()
        database.create_weight_entry(weight=70, user_id=USER_ID, date=date)

        self.created_at = date
        self.assertTrue(User.objects.filter(user_id=USER_ID).exists())

    def test_save_meal(self):
        self.assertTrue(Meal.objects.filter(name="lasagna").exists())

    def test_save_weight(self):
        self.assertTrue(WeightEntry.objects.filter(date=self.created_at).exists())
        weight_entries = database.get_weightentries(USER_ID)
        weight_entries.filter(date=self.created_at)

    def test_save_meal_entry(self):
        date = datetime.datetime.now()
        database.create_meal_entry(user_id=USER_ID, meal_id=self.meal.id, date=date)

        self.assertTrue(MealEntry.objects.filter(user_id=USER_ID).exists(), "User has meal entries")
        self.assertTrue(MealEntry.objects.filter(meal__name="lasagna").exists(), "User has meal entry for lasagna")
        self.assertTrue(MealEntry.objects.filter(user_id=USER_ID, meal_id=self.meal.id).exists(),
                        "User has meal entry for lasagna")
        self.assertTrue(MealEntry.objects.filter(date=date).exists(), "")

        weight_entries = database.get_weightentries(USER_ID)
        weight_entries.filter(date=date)


class ClassifierTestCase(TestCase):
    def setUp(self):
        self.classifier = Classifier()

    def test_save_meal_classification(self):
        self.assertEqual(self.classifier.classify("Today i had a Wurstbrot"), Classifier.MEAL_SAVE)
        self.assertEqual(self.classifier.classify("I dined rice pudding"), Classifier.MEAL_SAVE)
        self.assertNotEqual(self.classifier.classify("Today is Monday"), Classifier.MEAL_SAVE)

    def test_save_weight_classification(self):
        self.assertEqual(self.classifier.classify("I weigh 71 kg"), Classifier.WEIGHT_SAVE)
        self.assertEqual(self.classifier.classify("I have 71 kg"), Classifier.WEIGHT_SAVE)
        self.assertEqual(self.classifier.classify("I am 71 kg heavy"), Classifier.WEIGHT_SAVE)
        self.assertNotEqual(self.classifier.classify("Today, i had an apple"), Classifier.WEIGHT_SAVE)
        self.assertNotEqual(self.classifier.classify("I ate two sandwiches"), Classifier.WEIGHT_SAVE)
        self.assertNotEqual(self.classifier.classify("Show me statistics for my weight"), Classifier.WEIGHT_SAVE)


class SaveMealWithAIMLTestCase(TestCase):
    def setUp(self):
        set_up_database()
        self.bot_comparison = chatbot.ComparisonChatBot(AIMLMessageHandler())
        self.bot_suggestion = chatbot.SuggestionChatBot(AIMLMessageHandler())
        self.bot_competition = chatbot.CompetitionChatBot(AIMLMessageHandler())
        self.bot_self_monitoring = chatbot.SelfMonitoringChatBot(AIMLMessageHandler())

    def test_bot_answer(self):
        message = "i ate apple pie"
        response = self.bot_comparison.respond(message, USER_ID)
        self.assertEqual(response, "The meal apple pie has been saved.")

    def test_meal_save(self):
        message = "i ate lasagna"
        self.bot_comparison.respond(message, USER_ID)

        user = User.objects.get(user_id=USER_ID)
        saved_meals = user.meal_entries.all()
        if not saved_meals:
            self.fail("No meals saved")
        self.assertEqual(saved_meals[0].meal.name, "lasagna")

    def test_weight_save(self):
        message = "i weigh 42kg"
        self.bot_comparison.respond(message, USER_ID)

        user = User.objects.get(user_id=USER_ID)
        saved_weights = user.weight_entries.all()
        if not saved_weights:
            self.fail("No weight entries present")
        self.assertEqual(saved_weights[0].weight, 42)


class SaveMealWithClassifierTestCase(TestCase):
    def setUp(self):
        set_up_database()

    def test_message_is_saved(self):
        message = "Today i had Wurstbrot"
        bot = ChatBot(message_handler=ClassificationMessageHandler())
        bot.respond(message, USER_ID)

        user = User.objects.get(user_id=USER_ID)
        saved_meals = user.meal_entries.filter(meal__name="Wurstbrot")

        self.assertNotEqual(len(saved_meals), 0)
