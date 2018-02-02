import datetime

import random

from .models import User, WeightEntry, RecipeEntry, MealEntry, Ingredient, Meal


def user_exists(user_id):
    return User.objects.filter(user_id=user_id).exists()


def user_has_gametype(user_id):
    return not _is_none(get_user(user_id), 'gametype')


def get_gametype(user_id):
    return get_user(user_id).gametype


def increase_initiation_step(user_id):
    user = get_user(user_id)
    user.initiation_step += 1
    user.save()


def save_user(user_id, first_name):
    return _create(User, user_id=user_id, first_name=first_name)


def get_initiation_step(user_id):
    return get_user(user_id).initiation_step


def user_has_height(user_id):
    return not _is_none(get_user(user_id), 'height')


def _is_none(model, attribute):
    return getattr(model, attribute) is None


def create_meal_entry(user_id, meal_id, date):
    return _create(MealEntry, user_id=user_id, meal_id=meal_id, date=date)


def create_recipe_entry(user_id, recipe_id, date):
    return _create(RecipeEntry, user_id=user_id, recipe_id=recipe_id, date=date)


def create_meal(name, calories, protein, fat, carbs):
    return _create(Meal, name=name, calories=calories, protein=protein, fat=fat, carbs=carbs)


def create_weight_entry(user_id, date, weight):
    return _create(WeightEntry, user_id=user_id, date=date, weight=float(weight))


def _create(clz, **kwargs):
    object_to_save = clz(**kwargs)
    object_to_save.save()
    return object_to_save


def get_last_recipeentry(user_id):
    print("___________get last recipeentry")
    if RecipeEntry.objects.filter(user_id=user_id).count() is 0:
        return None
    print(RecipeEntry.objects.filter(user_id=user_id).latest("date"))
    return RecipeEntry.objects.filter(user_id=user_id).latest("date")


def get_last_mealentry(user_id):
    if MealEntry.objects.filter(user_id=user_id).count() is 0:
        return None
    return MealEntry.objects.filter(user_id=user_id).latest("date")


def get_latest_weightentry(user_id):
    if WeightEntry.objects.filter(user_id=user_id).count() is 0:
        return None
    return WeightEntry.objects.filter(user_id=user_id).latest("date")


def get_mealentries(user_id):
    return get_user(user_id).meal_entries.all()


def get_weightentries(user_id):
    return get_user(user_id).weight_entries.all()


def get_user(user_id):
    return User.objects.get(user_id=user_id)


def get_calories_day(user_id, date=datetime.datetime.now().date()):
    end_date = date + datetime.timedelta(days=1)
    # meal_entry_calories = get_user(user_id).meal_entries.filter(date__range=(date, end_date)).values("meal__calories")
    recipe_entries = RecipeEntry.objects.filter(user=user_id, date__range=(date, end_date))
    energy_sum = 0
    for recipe_entry in recipe_entries:
        recipe_ingredients = Ingredient.objects.filter(recipe=recipe_entry.recipe)
        for ingredient in recipe_ingredients:
            energy_sum += ingredient.energy

    calories = energy_sum / 4.187
    # for item in meal_entry_calories:
    # calories += item["meal__calories"]

    return calories


def get_calories_week(user_id, start=None, end=None):
    now = datetime.datetime.now()
    if not start and not end:
        start = now - datetime.timedelta(days=now.weekday())
    else:
        if not end:
            start = start - datetime.timedelta(days=start.weekday())
    end = start + datetime.timedelta(days=6)

    # calories = 0
    # calories_set = MealEntry.objects.filter(
    #     user=user_id, date__range=(start, end)).values("meal__calories")
    # for item in calories_set:
    #     calories = calories + item["meal__calories"]

    recipe_entries = RecipeEntry.objects.filter(user=user_id, date__range=(start, end))
    energy_sum = 0
    for recipe_entry in recipe_entries:
        recipe_ingredients = Ingredient.objects.filter(recipe=recipe_entry.recipe)
        for ingredient in recipe_ingredients:
            energy_sum += ingredient.energy
    calories = energy_sum / 4.187
    return calories


def get_meals_day(user_id, date=datetime.datetime.now().date()):
    end_date = date + datetime.timedelta(days=1)
    recipe_entries = RecipeEntry.objects.filter(user=user_id, date__range=(date, end_date))

    meal_names = list()
    for recipe_entry in recipe_entries:
        meal_names.append(recipe_entry.recipe.name)
    return ", ".join(meal_names)


def get_recipes_day(user_id, date=datetime.datetime.now().date()):
    end_date = date + datetime.timedelta(days=1)
    recipe_entries = RecipeEntry.objects.filter(user=user_id, date__range=(date, end_date))
    recipe_names = list()
    for recipe in recipe_entries:
        recipe_names.append(recipe.meal.name)
    return ", ".join(recipe_names)


def get_last_calories(user_id):
    if RecipeEntry.objects.filter(user_id=user_id).count() is 0:
        return None
    recipe = RecipeEntry.objects.filter(user_id=user_id).latest("date").recipe
    recipe_ingredients = Ingredient.objects.filter(recipe=recipe)

    energy_sum = 0
    for ingredient in recipe_ingredients:
        energy_sum += ingredient.energy

    # kJ to kcal
    calories = kj_to_kcal(energy_sum)
    return calories


def get_all_user():
    user_set = User.objects.all().values_list("user_id")
    users = []
    for item in user_set:
        users.append(item[0])
    return users


def get_suggestion_users():
    user_set = User.objects.filter(gametype="suggestion").values_list("user_id")
    users = []
    for item in user_set:
        users.append(item)
    return users


def get_self_monitoring_users():
    user_set = User.objects.filter(gametype="self-monitoring").values_list("user_id")
    users = []
    for item in user_set:
        users.append(item)
    return users


def get_comparison_users():
    user_set = User.objects.filter(gametype="comparison").values_list("user_id")
    users = []
    for item in user_set:
        users.append(item)
    return users


def get_competition_users():
    user_set = User.objects.filter(gametype="competition").values_list("user_id")
    users = []
    for item in user_set:
        users.append(item)
    return users


def get_random_user(user_id):
    users = User.objects.all().exclude(user_id=user_id).values_list('user_id')
    id = random.choice(users)
    return id[0]


def get_user_name_by_id(user_id):
    name = User.objects.filter(user_id=user_id).values("first_name")
    return name[0]["first_name"]


def get_average_calories(user_id, start=None, end=None):
    if not start and not end:
        recipe_entries = RecipeEntry.objects.filter(user_id=user_id)
    else:
        if not end:
            end = datetime.datetime.now().date() + datetime.timedelta(days=1)
        recipe_entries = RecipeEntry.objects.filter(user_id=user_id, date__range=(start, end))

    energy_sum = 0
    for item in recipe_entries:
        for ingredient in item.ingredients:
            energy_sum += ingredient.energy

    # kJ to kcal
    calories = kj_to_kcal(energy_sum)

    if len(recipe_entries) is not 0:
        return calories / len(recipe_entries)
    return 0


def kj_to_kcal(energy):
    return energy / 4.186
