import datetime

import aiml
import re
from os import listdir
from fuzzywuzzy import fuzz

from nombot import utils
from nombot.classification import NounExtractor
from .models import WeightEntry, User, RecipeEntry, Recipe
from . import database
from nombot import telegram
from nombot import plotter
import nuqui

STANDARD = "standard"
SUGGESTION = "suggestion"
SELF_MONITORING = "self-monitoring"
COMPARISON = "comparison"
COMPETITION = "competition"

KERNELS = {
    STANDARD: None,
    SUGGESTION: None,
    SELF_MONITORING: None,
    COMPARISON: None,
    COMPETITION: None
}

INIT_GAMETYPE = "gametype"
INIT_WEIGHT = "weight"
INIT_HEIGHT = "height"
INIT_GENDER = "sex"

INITIATION_STEPS = [
    {
        "message": "Welcher Spieltyp passt am ehesten zu dir?",
        "type": INIT_GAMETYPE
    },
    {
        "message": "Wie viel wiegst du gerade (in kg)?",
        "type": INIT_WEIGHT
    },
    {
        "message": "Wie groß bist du (in cm)?",
        "type": INIT_HEIGHT
    },
    {
        "message": "Welches Geschlecht hast du?",
        "type": INIT_GENDER
    }
]


def _get_initiation_step(type):
    for step in INITIATION_STEPS:
        if step['type'] == type:
            return step
    return None


class AIMLMessageHandler:
    RESPONSE_PATTERN_MEAL_SAVED = "Ich habe deine Mahlzeit\s.*\sgespeichert."
    RESPONSE_PATTERN_WEIGHT_SAVED = "Ich habe dein Gewicht von\s.*\sgespeichert."
    MESSAGE_PATTERN_CAL_HISTORY = "kalorien verlauf"
    MESSAGE_PATTERN_WEIGHT_HISTORY = "gewicht verlauf"
    MESSAGE_PATTERN_QUIZ_ANSWER_A = "!A"
    MESSAGE_PATTERN_QUIZ_ANSWER_B = "!B"
    MESSAGE_PATTERN_QUIZ_ANSWER_C = "!C"
    MESSAGE_PATTERN_QUIZ_ANSWER_D = "!D"

    def _handle_save_meal_response(self, response, kernel, user):
        meal_name = kernel.getPredicate("last_meal", user.user_id)
        # saved_meals = Meal.objects.all()
        saved_meals = Recipe.objects.all()

        raw_message_ratios = {}
        noun_message_ratios = {}

        for meal in saved_meals:
            raw_message_ratios[meal] = fuzz.partial_ratio(meal_name, meal.name)
            extractor = NounExtractor()
            nouns = " ".join(extractor.extract(meal_name))
            noun_message_ratios[meal] = fuzz.token_set_ratio(nouns, meal.name)

        best_match = None
        highest_ratio = None

        for meal, ratio in raw_message_ratios.items():
            if not highest_ratio or ratio > highest_ratio:
                highest_ratio = ratio
                best_match = meal

        if highest_ratio is not None and highest_ratio > 66:
            user = User.objects.get(user_id=user.user_id)

            # meal_entry = MealEntry()
            # meal_entry.date = datetime.datetime.now()
            # meal_entry.meal = best_match
            # meal_entry.user = user
            # meal_entry.save()

            recipe_entry = RecipeEntry()
            recipe_entry.date = datetime.datetime.now()
            recipe_entry.recipe = best_match
            recipe_entry.user = user
            recipe_entry.save()

    def handle_response(self, response, kernel, user):
        if re.match(self.RESPONSE_PATTERN_MEAL_SAVED, response, re.IGNORECASE):
            self._handle_save_meal_response(response, kernel, user)
        elif re.match(self.RESPONSE_PATTERN_WEIGHT_SAVED, response, re.IGNORECASE):
            self._handle_save_weight_response(response, kernel, user)
        self._sync_predicates(kernel, user)

    def handle_message(self, message, kernel, user):
        if re.match(self.MESSAGE_PATTERN_CAL_HISTORY, message, re.IGNORECASE):
            self._handle_cal_history(message, kernel, user)
        elif re.match(self.MESSAGE_PATTERN_WEIGHT_HISTORY, message, re.IGNORECASE):
            self._handle_weight_history(message, kernel, user)
        self._sync_predicates(kernel, user)

    def is_quiz_answer(self, message): 
        if re.match(self.MESSAGE_PATTERN_QUIZ_ANSWER_A, message, re.IGNORECASE):
            return True
        elif re.match(self.MESSAGE_PATTERN_QUIZ_ANSWER_B, message, re.IGNORECASE):
            return True
        elif re.match(self.MESSAGE_PATTERN_QUIZ_ANSWER_C, message, re.IGNORECASE):
            return True
        elif re.match(self.MESSAGE_PATTERN_QUIZ_ANSWER_D, message, re.IGNORECASE):
            return True
        else:
            return False


    def _sync_predicates(self, kernel, user):
        last_recipe_entry = database.get_last_recipeentry(user.user_id)
        if last_recipe_entry is not None:
            kernel.setPredicate("last_meal", last_recipe_entry.recipe.name, user.user_id)

        kernel.setPredicate("meals_today", database.get_meals_day(user.user_id), user.user_id)

        last_weight_entry = database.get_latest_weightentry(user.user_id)
        if last_weight_entry is not None:
            kernel.setPredicate("last_weight", str(last_weight_entry.weight), user.user_id)
            kernel.setPredicate("last_weight_date", last_weight_entry.date.strftime("%d. %B %Y"), user.user_id)

        kernel.setPredicate("user_name", user.get_name(), user.user_id)

        last_calories = database.get_last_calories(user.user_id)
        if last_calories is not None:
            kernel.setPredicate("kcal_last", str(last_calories), user.user_id)
        kernel.setPredicate("kcal_today", str(int(round(database.get_calories_day(user.user_id)))), user.user_id)

        kernel.setPredicate(
            "kcal_yesterday",
            str(int(round(database.get_calories_day(user.user_id,
                                                    date=(
                                                    datetime.datetime.now().date() - datetime.timedelta(days=1)))))),
            user.user_id
        )

        kernel.setPredicate("kcal_week", str(int(round(database.get_calories_week(user.user_id)))), user.user_id)

        start = datetime.datetime.now() - datetime.timedelta(days=6)
        kernel.setPredicate("kcal_last_week", str(int(round(database.get_calories_week(user.user_id, start=start)))),
                            user.user_id)
        # kernel.setPredicate("kcal_average_daily", str(database.get_average_calories(user.user_id)), user.user_id)

        # Random User:
        random_user_id = database.get_random_user(user.user_id)
        random_user_name = database.get_user_name_by_id(random_user_id)
        kernel.setPredicate("random_name", random_user_name, random_user_id)
        kernel.setPredicate("kcal_today_random", str(int(round(database.get_calories_day(random_user_id)))),
                            random_user_id)
        kernel.setPredicate(
            "kcal_yesterday",
            str(int(round(database.get_calories_day(random_user_id,
                                                    date=(
                                                    datetime.datetime.now().date() - datetime.timedelta(days=1)))))),
            random_user_id
        )

        kernel.setPredicate("kcal_week", str(int(round(database.get_calories_week(random_user_id)))), random_user_id)

    
    def handle_quiz_request(self, user):
        #get a question
        question_dict = nuqui.get_predefined_question_dict_with_random_answers(user.user_id)
        message = "*Question*: \n" + question_dict['question'] + "\n*Value*:\n " + str(question_dict['value']) +  "\n\n*Answers*:\n" + "A: "+question_dict['answer'][0] + "\nB: "+question_dict['answer'][1] + "\nC: "+question_dict['answer'][2] + "\nD: "+question_dict['answer'][3]
        #send it to telegram
        telegram.send_quiz(user.user_id, message)


    def _handle_save_weight_response(self, response, kernel, user):
        weight_predicate = kernel.getPredicate("last_weight", user.user_id)
        numbers = utils.extract_numbers(weight_predicate)

        if len(numbers) is not 1:
            print("There were several numbers: " + str(numbers))
            return

        weight_entry = WeightEntry()
        weight_entry.date = datetime.datetime.now()
        weight_entry.user = user
        weight_entry.weight = float(numbers[0])
        weight_entry.save()

    def _handle_weight_history(self, message, kernel, user):
        #image_id = plotter.plot_weight_history(user.user_id)
        #file = {'photo': open("nombot/data/" + str(image_id) + ".png", 'rb')}
        #telegram.send_photo(file, user_id=user.user_id)
        telegram.send_message("Function not availalbe", user.user_id)

    def _handle_cal_history(self, message, kernel, user):
        #image_id = plotter.plot_daily_calories(user.user_id)
        #file = {'photo': open("nombot/data/" + str(image_id) + ".png", 'rb')}
        #telegram.send_photo(file, user_id=user.user_id)
        telegram.send_message("Function not availalbe", user.user_id)


def _load_standard_aiml_files(kernel):
    files = (listdir("nombot/aimllib/standard"))
    for f in files:
        kernel.learn("nombot/aimllib/standard/" + f)


def _init_kernels():
    for gametype in KERNELS:
        if not KERNELS[gametype]:
            kernel = aiml.Kernel()
            kernel.learn("nombot/aimllib/gametypes/base.aiml")
            kernel.learn("nombot/aimllib/gametypes/german.aiml")
            if gametype is not STANDARD:
                kernel.learn("nombot/aimllib/gametypes/" + gametype + ".aiml")
            KERNELS[gametype] = kernel


class ChatBot:
    def __init__(self, gametype=STANDARD, message_handler=None):
        _init_kernels()
        self._kernel = KERNELS[gametype]
        self.message_handler = message_handler

    def react_to_initiation(self, user_id, data):
        received_message = data['message']['text']
        user = database.get_user(user_id)

        current_step = INITIATION_STEPS[database.get_initiation_step(user_id)]

        if current_step['type'] is INIT_GAMETYPE:
            types = [
                COMPETITION,
                COMPARISON,
                SELF_MONITORING,
                SUGGESTION
            ]

            if received_message in types:
                user.gametype = received_message
                user.save()
                telegram.send_weight_selection(user_id, _get_initiation_step(INIT_WEIGHT)['message'])

            else:
                telegram.send_gametype_selection(user_id, current_step['message'])
                return

        elif current_step['type'] is INIT_WEIGHT:
            numbers = utils.extract_numbers(received_message)
            if len(numbers) == 0:
                telegram.send_weight_selection(user_id, "Das habe ich nicht verstanden. " + current_step['message'])
                return
            else:
                database.create_weight_entry(user_id, datetime.datetime.now(), float(numbers[0]))
                telegram.send_message("Dein Gewicht wurde gespeichert.", user_id, close_keyboard=True)
                telegram.send_height_selection(user_id, _get_initiation_step(INIT_HEIGHT)['message'])

        elif current_step['type'] is INIT_HEIGHT:
            numbers = utils.extract_numbers(received_message)
            if len(numbers) == 0:
                telegram.send_height_selection(user_id, "Das habe ich nicht verstanden. " + current_step['message'])
                return
            else:
                height = numbers[0]
                user.height = height
                user.save()
                telegram.send_message("Deine Größe von %dcm wurde gespeichert." % user.height,
                                      user_id, close_keyboard=True)
                telegram.send_gender_selection(user_id, _get_initiation_step(INIT_GENDER)['message'])

        elif current_step['type'] is INIT_GENDER:
            user.gender = received_message
            user.save()
            telegram.send_message("Dein Geschlecht wurde gespeichert.", user_id, close_keyboard=True)

        database.increase_initiation_step(user_id)


    def react_to_quiz(self, user):
        if self.message_handler is not None:
            self.message_handler.handle_quiz_request(user)

    
    def is_quiz_answer(self, message):
        if self.message_handler is not None:
            return self.message_handler.is_quiz_answer(message)
        else:
            return False

    def respond(self, message, user):
        if self.message_handler is not None:
            self.message_handler.handle_message(message, self._kernel, user)
        response = self._kernel.respond(message, user.user_id)
        if self.message_handler is not None:
            self.message_handler.handle_response(response, self._kernel, user)
        return self._kernel.respond(message, user.user_id)

    def set_predicate(self, name, value, session_id):
        self._kernel.setPredicate(name, str(value), session_id)


class SuggestionChatBot(ChatBot):
    def __init__(self, message_handler=None):
        super().__init__(gametype=SUGGESTION, message_handler=message_handler)


class SelfMonitoringChatBot(ChatBot):
    def __init__(self, message_handler=None):
        super().__init__(gametype=SELF_MONITORING, message_handler=message_handler)


class ComparisonChatBot(ChatBot):
    def __init__(self, message_handler=None):
        super().__init__(gametype=COMPARISON, message_handler=message_handler)


class CompetitionChatBot(ChatBot):
    def __init__(self, message_handler=None):
        super().__init__(gametype=COMPETITION, message_handler=message_handler)
