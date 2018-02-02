from textblob.classifiers import NaiveBayesClassifier
from textblob import TextBlob


class Classifier:
    MEAL_SAVE = 'meal_save'
    WEIGHT_SAVE = 'weight_save'
    WEIGHT_HISTORY = 'weight_history'
    CALORIES_DAILY = 'calories_daily'
    STATISTIC_TODAY = 'statistic_today'
    ETC = 'etc'

    train = [
        ('Today i had an apple', MEAL_SAVE),
        ('I ate a sandwich.', MEAL_SAVE),
        ('I had a sandwich.', MEAL_SAVE),
        ('I eat a sandwich.', MEAL_SAVE),
        ('I ate 2 bananas.', MEAL_SAVE),
        ('I had 2 steaks', MEAL_SAVE),
        ('I had an egg for breakfast.', MEAL_SAVE),
        ('For breakfast I had a sandwich.', MEAL_SAVE),
        ('For lunch I had a hamburger.', MEAL_SAVE),
        ('For dinner I had a kebab.', MEAL_SAVE),
        ('I ate a sandwich.', MEAL_SAVE),
        ('I ate pancake.', MEAL_SAVE),
        ('I dined soup.', MEAL_SAVE),
        ('Show me my weight diary.', WEIGHT_HISTORY),
        ('weight diary', WEIGHT_HISTORY),
        ('weight history.', WEIGHT_HISTORY),
        ('kilo diary.', WEIGHT_HISTORY),
        ('Show me my daily calories.', CALORIES_DAILY),
        ('This is my best work.', ETC),
        ('Hi', ETC),
        ('Hallo', ETC),
        ('What is ', ETC),
        ('Anything', ETC),
        ('I don\'t know what to say', ETC),
        ('I have a dog.', ETC),
        ('I had a cat.', ETC),
        ('I want to make a diet', ETC),
        ('I want to slim', ETC),
        ('I have 100 kilos', WEIGHT_SAVE),
        ('I have 100 kilo', WEIGHT_SAVE),
        ('I had 100 kilos', WEIGHT_SAVE),
        ('I had 50 kg.', WEIGHT_SAVE),
        ('My weight is 75 kg.', WEIGHT_SAVE),
        ('I had 60 kg.', WEIGHT_SAVE),
        ('I had 60 kilo.', WEIGHT_SAVE),
        ('I had 60 kgs.', WEIGHT_SAVE),
        ('I had 60 kilogram.', WEIGHT_SAVE),
        ('I had 60 kilogramme.', WEIGHT_SAVE),
        ('I had 60 kilograms.', WEIGHT_SAVE),
        ('I weigh 60 kg.', WEIGHT_SAVE),
        ('I\'m weighing 60 kg.', WEIGHT_SAVE),
        ('I am weighing 60 kg.', WEIGHT_SAVE),
        ('I weigh little 60 kg.', WEIGHT_SAVE),
        ('Please show me my weight history.', WEIGHT_HISTORY),
        ('Show me my weight history.', WEIGHT_HISTORY),
        ('Can you show me my weight history?', WEIGHT_HISTORY),
        ('I want to see my weight history.', WEIGHT_HISTORY),
        ('What is my weight history from this week?', WEIGHT_HISTORY),
        ('What were my daily calories from this week?', CALORIES_DAILY),
        ('What are my daily calories from this week?', CALORIES_DAILY),
        ('Show me the daily calories from this week!', CALORIES_DAILY),
        ('Give mi a list of calories from this week!', CALORIES_DAILY),
        ('I want to see a list of daily calories.', CALORIES_DAILY),
        ('Show me my meals from today.', STATISTIC_TODAY),
        ('Please show me my todays food.', STATISTIC_TODAY),
        ('Give me a list from my todays food.', STATISTIC_TODAY),
        ('List me my todays food.', STATISTIC_TODAY),
        ('Catalogue me my todays food.', STATISTIC_TODAY),
    ]

    def __init__(self):
        self.__classifier = NaiveBayesClassifier(self.train)

    def classify(self, text):
        return self.__classifier.classify(text)


def get_tagged_words(text):
    blob = TextBlob(text)
    return blob.pos_tags


class POSExtractor:
    def extract(self, text):
        raise NotImplementedError("Subclass should implement this.")


class NounExtractor(POSExtractor):
    def extract(self, text):
        return [tagged_word[0] for tagged_word in get_tagged_words(text) if tagged_word[1].startswith("NN")]


class NumberExtractor(POSExtractor):
    def extract(self, text):
        return [tagged_word[0] for tagged_word in get_tagged_words(text) if tagged_word[1].startswith("CD")]
