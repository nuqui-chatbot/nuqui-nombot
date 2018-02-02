from django.db import models


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, null=True)
    gender = models.CharField(max_length=10, null=True)
    height = models.IntegerField(null=True)
    gametype = models.CharField(max_length=20, null=True)
    initiation_step = models.IntegerField(default=0)

    def get_name(self):
        if self.last_name:
            return self.first_name + " " + self.last_name
        return self.first_name


class Meal(models.Model):
    name = models.CharField(max_length=255)
    calories = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()


class RecipeEntry(models.Model):
    recipe = models.ForeignKey('Recipe', related_name='recipe_entries')
    user = models.ForeignKey('User', related_name='recipe_entries')
    date = models.DateTimeField()


class MealEntry(models.Model):
    meal = models.ForeignKey('Meal', related_name='meal_entries')
    user = models.ForeignKey('User', related_name='meal_entries')
    date = models.DateTimeField()


class Recipe(models.Model):
    recipe_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)


class Ingredient(models.Model):
    ingredient_id = models.IntegerField()
    recipe = models.ForeignKey('Recipe', related_name='ingredients')
    fat = models.FloatField()
    carbohydrates = models.FloatField()
    protein = models.FloatField()
    name = models.CharField(max_length=255)
    energy = models.FloatField()


class WeightEntry(models.Model):
    user = models.ForeignKey('User', related_name='weight_entries')
    weight = models.FloatField()
    date = models.DateTimeField()
