import csv

from utils import get_resource_path

class Const:

    PLAYER_DICT = dict()

    with open(get_resource_path('resource/players.csv'), 'r', encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                key, value = row
                PLAYER_DICT[key] = value

    TEAM_LIST = list()

    with open(get_resource_path('resource/teams.csv'), 'r', encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 1:
                TEAM_LIST.append(row[0])

    ABILITY_LIST = list()

    with open(get_resource_path('resource/ability.csv'), 'r', encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 1:
                ABILITY_LIST.append(row[0])

    ABILITY_LIST1 = list()

    with open(get_resource_path('resource/ability1.csv'), 'r', encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 1:
                ABILITY_LIST1.append(row[0])