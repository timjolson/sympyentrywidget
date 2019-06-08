from entryWidget import EntryWidget
from copy import copy


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
