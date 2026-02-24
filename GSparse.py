import csv
import io
import urllib.request
import re


def GetGS(url):
    """
    Function to get the Google Sheet with timetable
    :param url: URL to get the Google Sheet
    :return: list of sheet's cells
    """
    response = urllib.request.urlopen(url + '/export?format=csv')
    rows = []
    with io.TextIOWrapper(response, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return rows


def getTimetableIndexes(rows):
    """
    Function to get the timetable indexes of rows and columns for each day and each group
    :param rows:
    :return: dictionaries with the timetable indexes for each day and each group
    """
    startRowInd = 0
    for i in range(len(rows)):
        if rows[i][0] != "":
            startRowInd = i
            break

    groupColumnIndexes = {}
    print(rows[startRowInd])
    for columnInd in range(len(rows[startRowInd])):
        groupNumber = re.match(r"Группа (\d+)", rows[startRowInd][columnInd])
        if groupNumber:
            groupColumnIndexes[groupNumber.group(1)] = columnInd

    dayRowIndexes = {}
    begin = startRowInd + 3
    end = 0
    day = rows[begin][0]
    for rowInd in range(begin, len(rows)):
        if rows[rowInd][0] != '':
            # +- 2 т.к. между днями есть пустые строки
            end = rowInd - 2
            dayRowIndexes[day] = [begin, end]
            begin = end + 2
            day = rows[rowInd][0]
        elif rowInd == len(rows) - 1:
            end = rowInd - 2
            dayRowIndexes[day] = [begin, end]
    return dayRowIndexes, groupColumnIndexes


def getMyTimetable(rowIndexes, groupIndex, rows):
    """
    Function to get the timetable for the Nth group's day
    :param rowIndexes: list of row indices for the row in the day
    :param groupIndex: index of the column for the group
    :param rows: list of cells from Google sheet
    :return: one string with the timetable for the Nth group's day'
    """
    """
    День недели rows[rowIndexes[0]][0]
    дата rows[rowIndexes[0]][1]
    время пары rows[rowIndexes][2]
    пара rows[rowIndexes][groupIndex]
    аудитория rows[rowIndexes][groupIndex+1]
    """
    timetable = (f'{rows[rowIndexes[0]][1]}\n'
                 f'{rows[rowIndexes[0]][0]}:\n'
                 f'\n')
    for rowInd in range(rowIndexes[0], rowIndexes[1]):
        if rows[rowInd][groupIndex] != '':
            timetable += rows[rowInd][2] + '\n'
            timetable += rows[rowInd][groupIndex] + '\n'
            if rows[rowInd][groupIndex + 1] != '':
                timetable += 'ауд. ' + rows[rowInd][groupIndex + 1] + '\n'
            timetable += '\n'
    return timetable
