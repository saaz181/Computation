from unittest import TestCase, expectedFailure
import dfa
import unittest
import exceptions


class Phase1Test(TestCase):
    def setUp(self) -> None:
        states = {'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9'}
        inputs = {'a', 'b'}
        transitions = {
                          'q0': {'a': 'q1', 'b': 'q9'},
                          'q1': {'a': 'q8', 'b': 'q2'},
                          'q2': {'a': 'q3', 'b': 'q2'},
                          'q3': {'a': 'q2', 'b': 'q4'},
                          'q4': {'a': 'q5', 'b': 'q8'},
                          'q5': {'a': 'q4', 'b': 'q5'},
                          'q6': {'a': 'q7', 'b': 'q5'},
                          'q7': {'a': 'q6', 'b': 'q5'},
                          'q8': {'a': 'q1', 'b': 'q3'},
                          'q9': {'a': 'q7', 'b': 'q8'},
                      }
        initial_state = 'q0'
        final_states = {'q3', 'q4', 'q9', 'q8'}

        self.strings_belong_to_dfa = ['abaaa', 'bb', 'aababab']
        self.is_empty = False
        self.is_finite = False

        self.dfa = dfa.DFA(states, inputs, transitions, final_states, initial_state)

    def test_accepting_string(self):
        accepted = []
        for input_string in self.strings_belong_to_dfa:
            compiled_string = self.dfa.accept_input(input_string)
            accepted.append(compiled_string)

        _pass = True
        for val in accepted:
            if not val:
                _pass = False

        self.assertEqual(_pass, True)

    def test_is_empty(self):
        self.assertEqual(self.dfa.is_empty(), self.is_empty)

    def test_is_finite(self):
        self.assertEqual(self.dfa.is_finite(), self.is_finite)

    @expectedFailure
    def test_length_infinite_language(self):
        length = 1
        self.assertEqual(self.dfa.__len__(), length)

    def test_length_finite_language(self):
        if not self.dfa.is_finite():
            self.skipTest('The Language is Not Finite')
        length = 2
        self.assertEqual(self.dfa.__len__(), length)

    def test_calc_shortest_word(self):
        shortest_word = 1
        self.assertEqual(self.dfa.shortest_word_length(), shortest_word)

    def test_longest_word(self):
        if not self.dfa.is_finite():
            self.skipTest('The Language is Not Finite')
        pass

    def test_complement(self):
        pass