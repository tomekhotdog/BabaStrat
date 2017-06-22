import operator
from frameworkExtensions import indicators as inds

NOT = 'not'
AND = 'and'
OR = 'or'
LT = '<'
LE = '<='
GT = '>'
GE = '>='
EQ = '=='
NE = '!='
MUL = '*'
DIV = '/'
ADD = '+'
SUB = '-'
POW = '**'

indicators = {'Price': inds.Price(),
              '7DaySMA': inds._7DaySMA(),
              '20DaySMA': inds._20DaySMA(),
              '50DaySMA': inds._50DaySMA(),
              '100DaySMA': inds._100DaySMA(),
              '200DaySMA': inds._200DaySMA(),
              '20DayEMA': inds._20DayEMA(),
              '50DayEMA': inds._50DayEMA(),
              '100DayEMA': inds._100DayEMA(),
              'DayHigh': inds.DayHigh(),
              'DayLow': inds.DayLow(),
              'Close': inds.Close(),
              'Pivot': inds.Pivot(),
              'R1': inds.R1(),
              'R2': inds.R2(),
              'R3': inds.R3(),
              'S1': inds.S1(),
              'S2': inds.S2(),
              'S3': inds.S3(),
              'WoodiePivot': inds.WoodiePivot(),
              'WoodieR1': inds.WoodieR1(),
              'WoodieR2': inds.WoodieR2(),
              'WoodieS1': inds.WoodieS1(),
              'WoodieS2': inds.WoodieS2(),
              'FibonacciR1': inds.FibonacciR1(),
              'FibonacciR2': inds.FibonacciR2(),
              'FibonacciR3': inds.FibonacciR3(),
              'FibonacciS1': inds.FibonacciS1(),
              'FibonacciS2': inds.FibonacciS2(),
              'FibonacciS3': inds.FibonacciS3(),
              'CamarillaR1': inds.CamarillaR1(),
              'CamarillaR2': inds.CamarillaR2(),
              'CamarillaR3': inds.CamarillaR3(),
              'CamarillaS1': inds.CamarillaS1(),
              'CamarillaS2': inds.CamarillaS2(),
              'CamarillaS3': inds.CamarillaS3()
              }


class MacroElement:
    def __init__(self, identifier):
        self.identifier = identifier


class MacroRule:
    def __init__(self, expr_string):
        elements = expr_string.split(' ')

        if ':-' not in elements:
            raise MacroElementParseException('Could not parse invalid MacroRule (does not contain :-)')

        operator_index = elements.index(':-')
        self.macroRuleHead = MacroElement(' '.join(elements[:operator_index]).strip())  # MacroElement
        self.macroRuleBody = MacroBooleanExpr(' '.join(elements[operator_index + 1:]).strip())  # MacroBooleanExpr

    def calculate(self, data_set, datetime):
        try:
            result = self.macroRuleBody.calculate(data_set, datetime)
        except TypeError:
            raise MacroRuleCalculationError('Macro Rule calculation error')
        return result


class MacroBooleanOperator:
    def __init__(self, operator_string):
        self.operator = self.parse(operator_string)

    def parse(self, operator_string):
        if operator_string == AND:
            return operator.and_
        elif operator_string == OR:
            return operator.or_
        elif operator_string == NOT:
            return operator.not_
        elif operator_string == '<=':
            return operator.le
        elif operator_string == '<':
            return operator.lt
        elif operator_string == '>=':
            return operator.ge
        elif operator_string == '>':
            return operator.gt
        elif operator_string == '==':
            return operator.eq
        elif operator_string == '!=':
            return operator.ne
        else:
            raise MacroElementParseException("Tried to parse invalid MacroBooleanOperator")

    def calculate(self, operand_1, operand_2):
        if self.operator == operator.not_:
            return self.operator(operand_1)

        return self.operator(operand_1, operand_2)


class MacroExprOperator:
    def __init__(self, operator_string):
        self.operator = self.parse(operator_string)

    def parse(self, operator_string):
        if operator_string == MUL:
            return operator.mul
        elif operator_string == DIV:
            return operator.truediv
        elif operator_string == ADD:
            return operator.add
        elif operator_string == SUB:
            return operator.sub
        elif operator_string == POW:
            return operator.pow
        else:
            raise MacroElementParseException("Tried to parse invalid MacroExprOperator: " + operator_string)

    def calculate(self, operand_1, operand_2):
        return self.operator(operand_1, operand_2)


class MacroExpr:
    def __init__(self, expr_string):
        self.expression = None
        self.operator = None
        self.operand_1 = None
        self.operand_2 = None

        elements = expr_string.split(' ')
        if expr_string in indicators:
            self.expression = indicators[expr_string]
        elif len(elements) > 0 and (MUL in elements or DIV in elements or ADD in elements or SUB in elements):
            if MUL in elements:
                operator_index = elements.index(MUL)
            elif DIV in elements:
                operator_index = elements.index(DIV)
            elif ADD in elements:
                operator_index = elements.index(ADD)
            elif SUB in elements:
                operator_index = elements.index(SUB)
            elif POW in elements:
                operator_index = elements.index(POW)
            else:
                raise MacroElementParseException('Could not parse MacroExpr operator: ' + expr_string)

            self.operator = MacroExprOperator(elements[operator_index])
            self.operand_1 = MacroExpr(' '.join(elements[:operator_index]).strip())
            self.operand_2 = MacroExpr(' '.join(elements[operator_index + 1:]).strip())
        else:
            try:
                self.expression = float(expr_string)
            except ValueError:
                raise MacroElementParseException('Could not parse MacroExpr (neither an indicator or float): ' + expr_string)

    def calculate(self, dataset, datetime):
        if isinstance(self.expression, float):
            return self.expression
        elif self.operand_1 is not None and self.operand_2 is not None:
            return self.operator.calculate(self.operand_1.calculate(dataset, datetime),
                                           self.operand_2.calculate(dataset, datetime))
        else:
            return self.expression.calculate(dataset, datetime)


class MacroBooleanExpr:
    def __init__(self, expr_string):
        self.operator = None
        self.operand_1 = None
        self.operand_2 = None

        elements = expr_string.split(' ')
        if NOT in elements and elements[0] == NOT:
            self.operator = MacroBooleanOperator(elements[0])
            self.operand_1 = MacroBooleanExpr(' '.join(elements[1:]).strip())

        elif AND in elements:
            operator_index = elements.index(AND)
            self.operator = MacroBooleanOperator(elements[operator_index])
            self.operand_1 = MacroBooleanExpr(' '.join(elements[:operator_index]).strip())
            self.operand_2 = MacroBooleanExpr(' '.join(elements[operator_index + 1:]).strip())

        elif OR in elements:
            operator_index = elements.index(OR)
            self.operator = MacroBooleanOperator(elements[operator_index])
            self.operand_1 = MacroBooleanExpr(' '.join(elements[:operator_index]).strip())
            self.operand_2 = MacroBooleanExpr(' '.join(elements[operator_index + 1:]).strip())

        elif LT in elements or LE in elements or GT in elements or GE in elements or EQ in elements or NE in elements:
            operator_index = 0
            if LT in elements:
                operator_index = elements.index(LT)
            if LE in elements:
                operator_index = elements.index(LE)
            if GT in elements:
                operator_index = elements.index(GT)
            if GE in elements:
                operator_index = elements.index(GE)
            if EQ in elements:
                operator_index = elements.index(EQ)
            if NE in elements:
                operator_index = elements.index(NE)

            self.operator = MacroBooleanOperator(elements[operator_index])
            self.operand_1 = MacroExpr(' '.join(elements[:operator_index]).strip())
            self.operand_2 = MacroExpr(' '.join(elements[operator_index + 1:]).strip())
        else:
            raise MacroElementParseException('Could not parse MacroBooleanExpr: ' + expr_string)

    def calculate(self, data_set, datetime):
        operand_1_result = self.operand_1.calculate(data_set, datetime) if self.operand_1 is not None else 0
        operand_2_result = self.operand_2.calculate(data_set, datetime) if self.operand_2 is not None else 0
        return self.operator.calculate(operand_1_result, operand_2_result)


class MacroElementParseException(Exception):
    def __init__(self, message):
        self.message = message


class MacroRuleCalculationError(Exception):
    def __init__(self, message):
        self.message = message