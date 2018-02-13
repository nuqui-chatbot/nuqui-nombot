import csv
import json

import io
from rest_framework.parsers import BaseParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

import nombot.utils as utils
from nombot.classification import Classifier
from nombot.models import Meal, User, Recipe, Ingredient
from nombot import telegram
from nombot import chatbot
from nombot import database
from nombot.strings import *
from nuqui import create_user, evaluate, remove_user
import re


class MealCsvParser(BaseParser):
    """
    CSV parser that reads meal data. Accepts column types in the following order:
    'name', 'calories', 'protein', 'fat', 'carbs'
    """
    media_type = 'text/csv'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Returns a list of WifiData Objects.
        """
        body = stream.read().decode(stream.encoding) if stream.encoding else stream.read().decode('UTF-8')
        reader = csv.DictReader(io.StringIO(body),
                                fieldnames=['name', 'calories', 'protein', 'carbs', 'fat'],
                                delimiter=",")

        rows = []
        for row in reader:
            rows.append(row)

        return rows


class IngredientsCsvParser(BaseParser):
    media_type = 'text/csv'

    def parse(self, stream, media_type=None, parser_context=None):
        body = stream.read().decode(stream.encoding) if stream.encoding else stream.read().decode('UTF-8')
        reader = csv.DictReader(io.StringIO(body),
                                fieldnames=['recipe_id', 'ingredient_id', 'name', 'matched_name',
                                            'percentage', 'portent', 'portion', 'energy', 'fat',
                                            'protein', 'carbohydrates', 'fibres', 'weight'],
                                delimiter="\t")

        rows = []
        for row in reader:
            rows.append(row)

        return rows


class RecipeCsvParser(BaseParser):
    media_type = 'text/csv'

    def parse(self, stream, media_type=None, parser_context=None):
        body = stream.read().decode(stream.encoding) if stream.encoding else stream.read().decode('UTF-8')
        reader = csv.DictReader(io.StringIO(body),
                                fieldnames=['recipe_id', 'ckid', 'name', 'timerequired', 'skillrequired'],
                                delimiter="\t")

        rows = []
        for row in reader:
            rows.append(row)

        return rows


class RecipeView(APIView):
    parser_classes = (RecipeCsvParser,)

    def post(self, request):
        if not request.META['CONTENT_TYPE'] == 'text/csv':
            return Response('Only accepts POST with a content-type of text/csv')

        self._save_recipes(request.DATA)

        return Response()

    def _save_recipes(self, recipes_list):
        # remove all already saved meals
        for saved_recipe in Recipe.objects.all():
            saved_recipe.delete()

        recipes = []

        for row in recipes_list:
            recipe = Recipe()
            recipe.name = str(row['name'])
            recipe.recipe_id = int(row['recipe_id'])
            recipes.append(recipe)

        Recipe.objects.bulk_create(recipes)


class IngredientsView(APIView):
    parser_classes = (IngredientsCsvParser,)

    def post(self, request):
        if not request.META['CONTENT_TYPE'] == 'text/csv':
            return Response('Only accepts POST with a content-type of text/csv')

        self._save_ingredients(request.DATA)

        return Response()

    def _save_ingredients(self, ingredients_list):
        # remove all already saved meals
        for saved_ingredient in Ingredient.objects.all():
            saved_ingredient.delete()

        ingredients = []

        for row in ingredients_list:
            ingredient = Ingredient()
            ingredient.ingredient_id = int(row['ingredient_id'])
            ingredient.name = row['name']
            ingredient.fat = float(row['fat'])
            ingredient.carbohydrates = float(row['carbohydrates'])
            ingredient.protein = float(row['protein'])
            ingredient.energy = row['energy']

            ingredient.recipe = Recipe.objects.get(recipe_id=int(row['recipe_id']))

            ingredients.append(ingredient)

        Ingredient.objects.bulk_create(ingredients)


class HelloWorldView(APIView):
    def get(self, request):
        return Response("NOM NOM NOM NOM NOM")


class MealView(APIView):
    parser_classes = (MealCsvParser,)

    def post(self, request):

        if not request.META['CONTENT_TYPE'] == 'text/csv':
            return Response('Only accepts POST with a content-type of text/csv')

        self._save_meals(request.DATA)

        return Response()

    def _save_meals(self, meals_list):
        # remove all already saved meals
        for saved_meal in Meal.objects.all():
            saved_meal.delete()

        meals = []

        for row in meals_list:
            meal = Meal()
            meal.calories = float(utils.extract_numbers(row['calories'])[0])
            meal.name = row['name']
            meal.carbs = float(utils.extract_numbers(row['carbs'])[0])
            meal.fat = float(utils.extract_numbers(row['fat'])[0])
            meal.protein = float(utils.extract_numbers(row['protein'])[0])
            meals.append(meal)

        Meal.objects.bulk_create(meals)


class UpdatesView(APIView):
    parser_classes = (JSONParser,)

    def get(self, request):
        updates = telegram.get_updates()
        return Response("" + json.dumps(updates, sort_keys=True))


class EventView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dateformat = '%Y-%m-%d'
        self.classifier = Classifier()

        self.bot_suggestion = self._init_bot(chatbot.SuggestionChatBot)
        self.bot_monitoring = self._init_bot(chatbot.SelfMonitoringChatBot)
        self.bot_comparison = self._init_bot(chatbot.ComparisonChatBot)
        self.bot_competition = self._init_bot(chatbot.CompetitionChatBot)
        self.bot_standard = self._init_bot(chatbot.ChatBot)

    def _init_bot(self, clz):
        return clz(message_handler=chatbot.AIMLMessageHandler())

    def post(self, request):
        if request.DATA:
            # chat id is equivalent to the user_id in a chat with a single person
            user_id = request.DATA['message']['chat']['id']

            # Check if user exits, if not then prompt the user for his motivation type
            if not database.user_exists(user_id):
                user = User()
                user.user_id = user_id
                user_name = request.DATA['message']['from']['first_name']
                user.first_name = request.DATA['message']['from']['first_name']
                if 'last_name' in request.DATA.get('message', {}).get('from', {}):
                    user.last_name = request.DATA['message']['from']['last_name']
                    user_name = user_name + request.DATA['message']['from']['last_name']
                user.save()
                create_user(user_id, user_name)

                bot = self._get_bot()
                bot.react_to_initiation(user_id, request.DATA)

            # Check initiation step
            elif database.get_initiation_step(user_id) < len(chatbot.INITIATION_STEPS):
                bot = self._get_bot()
                bot.react_to_initiation(user_id, request.DATA)

            # User exists and no special case was met, send a normal AIML-Response to the user
            else:
                # load aiml-file according to motivation type
                gametype = database.get_gametype(user_id)
                bot = self._get_bot(gametype)
                user = database.get_user(user_id)
                if 'text' not in request.DATA['message']:
                    if 'Photo' in request.DATA['message']:
                        telegram.send_message("Nice photo!", user_id)
                    else:
                        telegram.send_message("Leider verstehe ich nur Textnachrichten.", user_id)
                    return Response()
                else:

                    received_message = request.DATA['message']['text']
                    if received_message == "/help":
                        telegram.send_message(HELP_FUNCTION, user_id)
                        return Response()
                    #just for testing and demonstration
                    #elif received_message == "/quiz":
                    #    bot.react_to_quiz(user)
                    #    return Response()
                    #elif bot.is_quiz_answer(received_message):
                        #nuqui check answer
                        msg = self._create_quiz_answer(evaluate(received_message, user_id))
                        telegram.send_message(msg, user_id)
                        return Response()
                    elif received_message == "/score":
                        bot.react_to_score(user)
                        return Response()
                    else:
                        telegram.send_message(bot.respond(received_message, user), user_id)

        return Response("Event received")


    def _get_bot(self, gametype=None):
        if gametype == "suggestion":
            return self.bot_suggestion
        elif gametype == "self-monitoring":
            return self.bot_monitoring
        elif gametype == "comparison":
            return self.bot_comparison
        elif gametype == "competition":
            return self.bot_competition
        else:
            return self.bot_standard


    def _create_quiz_answer(self, result_dict):
        message = ""
        if result_dict['success']:
            message += "*GRATULATION!!!!* '"+ result_dict['right_answer'] +"' was the right answer\nYou gain for this " + str(result_dict['achieved_points']) + " Points!!\n\n"+ "You have now " + str(result_dict['total_points']) + " Points!"
        else:
            message += "That was wrong :(...\n Better luck next time!\n\n You still have " + str(result_dict['total_points']) + " Points."
        return message
