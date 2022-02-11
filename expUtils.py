from enum import Enum
import re

class TOKEN_TYPE(Enum):
    LEFT_BR = 0
    RIGHT_BR = 1
    NOT = 2
    AND = 3
    OR = 4
    CONS = 5
    VAR = 6

class EXP_TYPE(Enum):
    UNARY = 0
    DOUBLE = 1
    VAR = 2


class Token:

    def __init__(self, gramType: TOKEN_TYPE, value: str):
        self.gramType = gramType
        self.value = value

    gramType: TOKEN_TYPE
    value: str



class Exp:

    def __init__(self, gramType: EXP_TYPE, parts: list):
        self.gramType = gramType
        self.parts = parts

    gramType: EXP_TYPE
    parts: list


tokenRegExs = {TOKEN_TYPE.LEFT_BR: "^\($",
               TOKEN_TYPE.RIGHT_BR: "^\)$",
               TOKEN_TYPE.NOT: "^!$",
               TOKEN_TYPE.AND: "^&$",
               TOKEN_TYPE.OR: "^\|$",
               TOKEN_TYPE.CONS: "^->$",
               TOKEN_TYPE.VAR: "^[A-Za-z]+[0-9]*$"
               }

def makeTokens(str):
    tokens = []
    i = len(str) + 1
    while i >= 0:
        for tokenRegEx in tokenRegExs.items():
            if re.match(tokenRegEx[1], str[0:i+1]):
                tokens.append(Token(tokenRegEx[0], str[0:i + 1]))
                str = str[i + 1: len(str)]
                i = len(str) + 1
                break
        i -= 1

    if len(str) != 0:
        raise Exception("Bad input string")
    else:
        return tokens

def makeExp(tokens: list):
    types = list(map(lambda tn: tn.gramType, tokens))

    while TOKEN_TYPE.LEFT_BR in types or TOKEN_TYPE.RIGHT_BR in types:
        mach = re.search("\([^(\(|\))]+\)", "".join(list(map(lambda
                    el: "(" if el == TOKEN_TYPE.LEFT_BR else ")" if el == TOKEN_TYPE.RIGHT_BR else "A",
            types))))

        if mach != None:
            rightIndex = mach.start()
            leftIndex = mach.end()
            exp = makeExp(tokens[rightIndex + 1: leftIndex - 1])
            tokens = tokens[0: rightIndex] + [exp] + tokens[leftIndex: len(tokens)]
            types = list(map(lambda tn: tn.gramType, tokens))

        else:
            raise Exception("Bad brackets")


    i = len(tokens) - 2
    while i >= 0:
        if types[i] == TOKEN_TYPE.NOT:
            if types[i + 1] == TOKEN_TYPE.VAR or type(tokens[i + 1]) == Exp:
                tokens[i + 1] = Exp(EXP_TYPE.UNARY, [tokens[i], tokens[i + 1]])
                tokens.pop(i)
                types[i + 1] = EXP_TYPE.UNARY
                types.pop(i)
            else:
                raise Exception("bad negation")
        i -= 1

    i = 1
    while i < len(tokens) - 1:
        if types[i] == TOKEN_TYPE.AND:
            if (types[i-1] == TOKEN_TYPE.VAR or type(tokens[i-1]) == Exp) and \
                    (types[i+1] == TOKEN_TYPE.VAR or type(tokens[i+1]) == Exp):
                tokens[i - 1] = Exp(EXP_TYPE.DOUBLE, [tokens[i - 1], tokens[i], tokens[i + 1]])
                types[i - 1] = EXP_TYPE.DOUBLE
                tokens.pop(i + 1)
                tokens.pop(i)
                types.pop(i + 1)
                types.pop(i)
            else:
                raise Exception("bad and")
        else:
            i += 1

    i = 1
    while i < len(tokens) - 1:
        if types[i] == TOKEN_TYPE.OR:
            if (types[i - 1] == TOKEN_TYPE.VAR or type(tokens[i - 1]) == Exp) and \
                    (types[i + 1] == TOKEN_TYPE.VAR or type(tokens[i + 1]) == Exp):
                tokens[i - 1] = Exp(EXP_TYPE.DOUBLE, [tokens[i - 1], tokens[i], tokens[i + 1]])
                types[i - 1] = EXP_TYPE.DOUBLE
                tokens.pop(i + 1)
                tokens.pop(i)
                types.pop(i + 1)
                types.pop(i)
            else:
                raise Exception("bad or")
        else:
            i += 1


    i = len(tokens) - 1
    while i >= 1:
        if types[i] == TOKEN_TYPE.CONS:
            if (types[i - 1] == TOKEN_TYPE.VAR or type(tokens[i - 1]) == Exp) and \
                    (types[i + 1] == TOKEN_TYPE.VAR or type(tokens[i + 1]) == Exp):
                tokens[i - 1] = Exp(EXP_TYPE.DOUBLE, [tokens[i - 1], tokens[i], tokens[i + 1]])
                types[i - 1] = EXP_TYPE.DOUBLE
                tokens.pop(i + 1)
                tokens.pop(i)
                types.pop(i + 1)
                types.pop(i)
                i -= 2
            else:
                raise Exception("bad cons")
        else:
            i -= 1


    if TOKEN_TYPE.VAR in types:
        if len(tokens) == 1:
            tokens[0] = Exp(EXP_TYPE.VAR, [tokens[0]])
            types[0] = EXP_TYPE.VAR
        else:
            raise Exception("bad exp")


    if len(tokens) == 1:
        return tokens[0]
    else:
        raise Exception("bad exp")

def getVarsRec(exp, varrs):
    if exp.gramType == TOKEN_TYPE.VAR:
        if exp.value not in varrs:
            varrs.append(exp.value)
    elif type(exp) == Exp:
        for part in exp.parts:
            varrs = getVarsRec(part, varrs)

    return varrs

def getVars(exp):
    return getVarsRec(exp, [])

def getLeftOperatorsRec(exp, s):
    if exp.gramType == EXP_TYPE.UNARY:
        s += "(!"
        s = getLeftOperatorsRec(exp.parts[1], s)
        s += ")"
        return s
    elif exp.gramType == EXP_TYPE.DOUBLE:
        s += "(" + exp.parts[1].value + ","
        s = getLeftOperatorsRec(exp.parts[0], s)
        s += ","
        s = getLeftOperatorsRec(exp.parts[2], s)
        s += ")"
        return s
    elif exp.gramType == EXP_TYPE.VAR:
        s += exp.parts[0].value()
        return s
    elif type(exp) == Token and exp.gramType == TOKEN_TYPE.VAR:
        s += exp.value
        return s
    else:
        raise Exception("bad exp")

def writeLeft(exp):
    print(getLeftOperatorsRec(exp, ""))

def makeExpFromStr(expr: str):
    return makeExp(makeTokens(expr))