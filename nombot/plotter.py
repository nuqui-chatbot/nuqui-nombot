# import matplotlib as mpl
#
# mpl.use('Agg')
#
# from matplotlib import pyplot as plt
# from matplotlib.dates import DayLocator, DateFormatter
# from django.db.models import Sum
# from uuid import uuid4
# import datetime
#
# from .models import WeightEntry, MealEntry, RecipeEntry, Ingredient
#
#
# def plot_weight_history(id):
#     try:
#         weight_set = WeightEntry.objects.filter(user=id).order_by('date').values_list('weight')
#         weights = []
#         datetimes = WeightEntry.objects.filter(user=id).order_by('date').values_list('date')
#         dates = mpl.dates.date2num(datetimes)
#         for weight in weight_set:
#             weights.append(weight[0])
#         days = DayLocator()
#         dayFmt = DateFormatter("%b %d %Y")
#
#         diagram = plt.subplot()
#         diagram.plot_date(dates, weights, linestyle="-", color="r")
#         diagram.xaxis.set_major_locator(days)
#         diagram.xaxis.set_major_formatter(dayFmt)
#         # plt.show()
#         plt.ylim(ymin=0)
#         plt.ylabel('weight(kg)')
#         plt.title("My weight history.")
#
#         image_id = uuid4()
#         plt.savefig('nombot/data/' + str(image_id) + '.png')
#         plt.close()
#
#         return image_id
#     except RuntimeError:
#         pass
#
#
# def plot_daily_calories(id):
#     try:
#         datetimes = []
#         calories = []
#
#         dates = RecipeEntry.objects.filter(user=id).order_by('date').values_list('date')
#         for date in dates:
#             formatted_date = datetime.date(date[0].year,date[0].month,date[0].day)
#             if formatted_date not in datetimes:
#                 datetimes.append(formatted_date)
#
#         for date in datetimes:
#             end_date = date + datetime.timedelta(days=1)
#             recipe_ids = RecipeEntry.objects.filter(user=id,date__range=(date,end_date)).values_list("recipe_id")
#             energy_sum = 0
#             for id in recipe_ids:
#                 recipe_ingredients = Ingredient.objects.filter(recipe= id)
#                 for ingredient in recipe_ingredients:
#                     energy_sum += ingredient.energy
#             calories.append(energy_sum / 4.187)
#
#         dates = mpl.dates.date2num(datetimes)
#         days = DayLocator()
#         dayFmt = DateFormatter("%b %d %Y")
#
#         diagram = plt.subplot()
#         diagram.plot_date(dates, calories, linestyle="-", color="r")
#         diagram.xaxis.set_major_locator(days)
#         diagram.xaxis.set_major_formatter(dayFmt)
#         # plt.show()
#         plt.ylim(ymin=0)
#         plt.ylabel('calories(kcal)')
#         plt.title("My daily calorie history.")
#
#         image_id = uuid4()
#         plt.savefig("nombot/data/" + str(image_id) + ".png")
#         plt.close()
#
#         return image_id
#     except RuntimeError:
#         pass
