# colorful.py

"""Offer colorful codeforces usernames and submissions"""

import datetime

__all__=['Colorful','ColorfulUser','ColorfulSubmission']

def CheckPair(item):
    return type(item) == list and len(item) == 2 and type(item[0]) == str and type(item[1]) == str

def calc_problemID(problem):
    if "contestId" in problem:
        return str(problem["contestId"]) + str(problem["index"])
    elif "problemsetName" in problem:
        return str(problem["problemsetName"]) + str(problem["index"])
    else:
        return str(problem["index"])

def FormatTime(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

def FormatStr(originStr, Length):
    if Length == -1:
        return originStr
    if len(originStr) <= Length:
        return originStr + ' ' * (Length - len(originStr))
    else:
        return originStr[:Length-3]+'...'


class Colorful:
    def __init__(self, Li=None):
        if Li is None:
            self.List = []
        elif type(Li) == Colorful:
            self.List=Li.List
        elif type(Li) == str:
            self.List=[[Li,'#A0ADB9']]
        else:
            if type(Li) != list:
                raise TypeError
            for item in Li:
                if not CheckPair(item):
                    raise TypeError
            self.List = Li
    def __add__(self, other):
        return Colorful(self.List+other.List)
    def __mul__(self, other):
        return Colorful(self.List*other)
    def __getitem__(self, item):
        return self.List[item]
    def __setitem__(self, item, value):
        self.List[item] = value
    def __repr__(self):
        return self.List
    def __len__(self):
        return len(self.List)
    def append(self, item):
        if type(item) == str:
            self.List.append([item,'#A0ADB9'])
        elif CheckPair(item):
            self.List.append(item)
        else:
            raise TypeError

def ColorfulUser(userName, rating, FormatLength = -1):
    userName=FormatStr(userName,FormatLength)
    if rating < 1200:
        color = '#808080'
    elif rating < 1400:
        color = '#008000'
    elif rating < 1600:
        color = '#03A89E'
    elif rating < 1900:
        color = '#0000FF'
    elif rating < 2100:
        color = '#AA0983'
    elif rating < 2300:
        color = '#FFCC88'
    elif rating < 2400:
        color = '#FF8C00'
    elif rating < 2600:
        color = '#FF0000'
    elif rating < 3000:
        color = '#FF2929'
    elif rating < 4000:
        color = '#FF0000'
    else:
        color = '#000000'
    if rating < 3000 or rating >= 4000:
        return Colorful([[userName,color]])
    else:
        return Colorful([[userName[0],'#000000'],[userName[1:],color]])

def ColorfulSubmission(userName, rating, submission,
                       FormatUserNameLength=-1, FormatProblemNameLength=-1, FormatProblemIdLength=-1):
    res = Colorful()
    problemID = FormatStr(calc_problemID(submission['problem']), FormatProblemIdLength)
    problemName = FormatStr(submission['problem']['name'], FormatProblemNameLength)
    submitTime = FormatTime(submission['creationTimeSeconds'])
    status = submission['verdict']
    passCases = submission['passedTestCount']
    res.append(f'At {submitTime}, ')
    res += ColorfulUser(userName, rating, FormatUserNameLength)
    res.append(f' submitted {problemID} {problemName} and ')
    match status:
        case 'OK':
            res.append(['Accepted','#00AA00'])
        case 'FAILED':
            res.append('Failed')
        case 'PARTIAL':
            res.append([f'Passed {passCases} testcases','#00AA00'])
        case 'COMPILATION_ERROR':
            res.append('Compilation error')
        case 'RUNTIME_ERROR':
            res.append([f'Runtime error on test {passCases + 1}','#673AB7'])
        case 'WRONG_ANSWER':
            res.append([f'Wrong answer on test {passCases + 1}','#673AB7'])
        case 'TIME_LIMIT_EXCEEDED':
            res.append([f'Time limit exceeded on test {passCases + 1}','#673AB7'])
        case 'MEMORY_LIMIT_EXCEEDED':
            res.append([f'Memory limit exceeded on test {passCases + 1}','#673AB7'])
        case 'IDLENESS_LIMIT_EXCEEDED':
            res.append([f'Idleness limit exceeded on test {passCases + 1}','#673AB7'])
        case 'REJECTED':
            res.append('Rejected')
        case 'SUBMITTED':
            res.append('In queue')
        case 'TESTING':
            res.append('Judging')
        case _:
            return res
    res.append('.')
    return res