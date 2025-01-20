import csv

class Const:

    CN_VER = False

    PLAYER_DICT = dict()

    with open('resource/players.csv', 'r', encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                key, value = row
                PLAYER_DICT[key] = value

    TEAM_LIST = list()

    with open('resource/teams.csv', 'r', encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 1:
                TEAM_LIST.append(row[0])

    CN_DICT = dict()

    with open('resource/cn.csv', 'r', encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                key, value = row
                CN_DICT[key] = value

    ABILITY_LIST = list()

    with open('resource/ability.csv', 'r', encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 1:
                ABILITY_LIST.append(row[0])

    ABILITY_LIST1 = list()

    with open('resource/ability1.csv', 'r', encoding='utf8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 1:
                ABILITY_LIST1.append(row[0])