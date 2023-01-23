import frozendict
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


# dfa = DFA(states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9'},
#               input_symbols={'a', 'b'},
#               transitions={
#                   'q0': {'a': 'q1', 'b': 'q9'},
#                   'q1': {'a': 'q8', 'b': 'q2'},
#                   'q2': {'a': 'q3', 'b': 'q2'},
#                   'q3': {'a': 'q2', 'b': 'q4'},
#                   'q4': {'a': 'q5', 'b': 'q8'},
#                   'q5': {'a': 'q4', 'b': 'q5'},
#                   'q6': {'a': 'q7', 'b': 'q5'},
#                   'q7': {'a': 'q6', 'b': 'q5'},
#                   'q8': {'a': 'q1', 'b': 'q3'},
#                   'q9': {'a': 'q7', 'b': 'q8'},
#               },
#               initial_state='q0',
#               final_states={'q3', 'q4', 'q9', 'q8'})
#

# minified_dfa = dfa.minify(retain_names=True)




# nfa = NFA(states={'q0', 'q1', 'q2'},
#     input_symbols={'a', 'b'},
#     transitions={
#         'q0': {'a': {'q1'}},
#         # Use '' as the key name for empty string (lambda/epsilon) transitions
#         'q1': {'a': {'q1'}, '': {'q2'}},
#         'q2': {'b': {'q0'}}
#     },
#     initial_state='q0',
#     final_states={'q1'})




# a = {frozenset({1, 2, 3}), frozenset({4, 5, 6}), frozenset({1, 4, 6}), frozenset({1})}

a = frozenset({'q2'})
b = {'q1', 'q3'}
print(len(a.intersection(b)))