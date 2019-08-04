from entrywidget import EntryWidget
from copy import copy
from sympy import S


test_strings = ['str0', 'str1', 'str2', ['not a string']]
test_options_good = ['opt1', 'opt2', 'opt3']
test_options_bad = ['opt1', ['not a string']]
test_options_colors = ['red', 'blue', 'green']
test_color_tuple = copy(EntryWidget.defaultColors['error'])
test_color_tuple_good = ('blue', 'white')
test_color_tuple_bad = ('blue', ['not a string'])
test_color_dict = copy(EntryWidget.defaultColors)
test_color_dict_good = copy(EntryWidget.defaultColors)
test_color_dict_good.update({'default': (test_color_tuple_good)})
test_color_dict_bad = copy(EntryWidget.defaultColors)
test_color_dict_bad.update({'default': (test_color_tuple_bad)})

# sample expressions to test
# ( expr, is_safe, causes error in sympy widgets, is valid identifier(variable name) )
expr_safe_check = [
    ('.a ', False, True, False),
    ('abc', True, False, True),
    ('1.1)', True, True, False),
    ('a)', True, True, False),
    ('1234a.', False, True, False),
    ('12a.a', False, True, False),
    ('1.a ', False, True, False),
    ('a.1 ', False, True, False),
    ('12a12.', False, True, False),
    ('2+4.1', True, False, False),
    ('a.a ', False, True, False),
    ('12a12.12a', False, True, False),
    ('.1 ', True, False, False),
    ('a.a', False, True, False),
    ('.a12', False, True, False),
    ('12a12.12', False, True, False),
    ('1212.a', False, True, False),
    ('ab.ab ', False, True, False),
    ('1212.12a', False, True, False),
    ('.ab ', False, True, False),
    ('a', True, False, True),
    ('.12a', False, True, False),
    ('1.ab ', False, True, False),
    ('error', True, False, True),
    ('ab.1 ', False, True, False),
    ('(a', True, True, False),
    ('1.1 ', True, False, False),
    ('a. ', False, True, False),
    ('12.12a', False, True, False),
    ('1. ', True, False, False),
    ('', True, False, False),
    ('ab. ', False, True, False),
    ('ab.', False, True, False),
    ('text', True, False, True),
    ('text_2', True, False, True),
    ('text2', True, False, True),
    ('text2a', True, False, True),
    ('text2.', False, True, False),
    ('(.1)', True, False, False),
    ('(1.)', True, False, False),
    ('1.)', True, True, False),
    ('cos(2) + sin', True, True, False),
    ('sin()', True, True, False),
    ('sin(pi/4)', True, False, False),
    ('sin(a)', True, False, False),
    ('sin(2)', True, False, False),
    ('sin', True, True, True),
]


# sample expressions to test
# ( expr, units are compatible )
units_work_check = [
    ('2 + 3*mm', False), ('1*mm + 2', False), ('5*mm + 2*kg', False), ('sin(2)*mm + exp(1)', False),
    ('mm*3 + 2', False), ('mm*3 + 2*pound', False), ('mm*3 + 2*N', False), ('1*inch + 2*mm**2', False),
    ('sin(pi)', True), ('sin(2)', True), ('1*mm', True), ('5*mm+1*inch', True),
    ('sin(2*mm/(1*inch))', True),
    # ('sin(2*mm/(1*inch)) + exp(1)', True)  # doesn't pass unitsAreConsistent without pre-processing
]

# sample expressions to test
# ( expr, target units, compatible, output )
units_convert_check = [
    ('sin(pi/2)', S.One, True, '1'),
    ('sin(pi/2)', 'inch', True, '1*inch'),
    ('sin(pi/4)', S.One, True, 'sqrt(2)/2'),
    ('sin(pi/4)', 'inch', True, 'inch*sqrt(2)/2'),
    ('1*mm', 'foot', True, '((5/127)/12)*foot'),
    ('1*mm', '1*pound', False, None),
    ('5*mm+1*inch', '1*foot', True, 'foot*(1+(25/127))/12'),
    ('5*mm+1*inch', '1*second', False, None),
    ('sin(2*mm/(1*inch))', S.One, True, 'sin(2/25.4)'),
    ('sin(2*mm/(1*inch))', 'foot', True, 'foot*sin(2/25.4)'),
]