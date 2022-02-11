from expUtils import makeExpFromStr, TOKEN_TYPE, EXP_TYPE, getVars
from enum import Enum



rools = {TOKEN_TYPE.NOT: {True: False, False: True},
         TOKEN_TYPE.AND: {(False, False): False, (False, True): False, (True, False): False, (True, True): True},
         TOKEN_TYPE.OR: {(False, False): False, (False, True): True, (True, False): True, (True, True): True},
         TOKEN_TYPE.CONS: {(False, False): True, (False, True): True, (True, False): False, (True, True): True}
         }

def valid(exp, assessment):
    if exp.gramType == EXP_TYPE.DOUBLE:
        left = valid(exp.parts[0], assessment)
        right = valid(exp.parts[2], assessment)
        return rools.get(exp.parts[1].gramType).get((left, right))
    elif exp.gramType == EXP_TYPE.UNARY:
        operand = valid(exp.parts[1], assessment)
        return rools.get(exp.parts[0].gramType).get(operand)
    elif exp.gramType == EXP_TYPE.VAR:
        var = exp.parts[0].value
        return assessment.get(var)
    elif exp.gramType == TOKEN_TYPE.VAR:
        var = exp.value
        return assessment.get(var)
    else:
        raise Exception("bad exception")

def estimate(exp):
    varrs = getVars(exp)
    assessments = []
    values = []

    for i in range(2 ** len(varrs)):
        assessment = {}
        comb = list(map(bool, map(int, list("0" * (len(varrs) - len(bin(i)[2:])) + bin(i)[2:]))))
        for j in range(len(comb)):
            assessment[varrs[j]] = comb[j]
        assessments.append(assessment)

    for assessment in assessments:
        values.append(valid(exp, assessment))

    if False in values and True in values:
        print("Satisfiable and invalid")
    elif True in values:
        print("Valid")
    else:
        print("Unsatisfiable")

exp = makeExpFromStr(input())
estimate(exp)

