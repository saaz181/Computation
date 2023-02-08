from nfa import NFA
import string


class Regex:
    def __init__(self, regex_expr):
        self.star = '*'
        self.plus = '+'
        self.dot = '.'
        self.openingBracket = '('
        self.closingBracket = ')'
        self.operators = [self.plus, self.dot]
        self.regex = regex_expr
        self.alphabet = string.ascii_letters + string.digits
        self.stack = []
        self.automata = []
        self.construct_nfa()

    @staticmethod
    def base_struct(input_symbol):
        state_1 = 1
        state_2 = 2
        basic = NFA(set(), dict(), set(), set(), set())
        basic.initial_state = state_1
        basic.final_states.add(state_2)

        basic.add_transition(1, 2, input_symbol)
        return basic

    @staticmethod
    def plus_struct(a, b):
        [a, m1] = a.build_from_number(2)
        [b, m2] = b.build_from_number(m1)
        state1 = 1
        state2 = m2
        plus = NFA(set(), dict(), set(), set(), set())
        plus.initial_state = state1
        plus.final_states.add(state2)

        plus.add_transition(plus.initial_state, a.initial_state, '')
        plus.add_transition(plus.initial_state, b.initial_state, '')
        plus.add_transition(list(a.final_states)[0], list(plus.final_states)[0], '')
        plus.add_transition(list(b.final_states)[0], list(plus.final_states)[0], '')
        plus.add_transition_dict(a.transitions)
        plus.add_transition_dict(b.transitions)
        return plus

    @staticmethod
    def dot_struct(a, b):
        [a, m1] = a.build_from_number(1)
        [b, m2] = b.build_from_number(m1)
        state1 = 1
        state2 = m2 - 1

        dot = NFA(set(), dict(), set(), set(), set())
        dot.initial_state = state1
        dot.final_states.add(state2)

        dot.add_transition(list(a.final_states)[0], b.initial_state, '')
        dot.add_transition_dict(a.transitions)
        dot.add_transition_dict(b.transitions)
        return dot

    @staticmethod
    def star_struct(a):
        [a, m1] = a.build_from_number(2)
        state1 = 1
        state2 = m1
        star = NFA(set(), dict(), set(), set(), set())
        star.initial_state = state1
        star.final_states.add(state2)

        star.add_transition(star.initial_state, a.initial_state, '')
        star.add_transition(star.initial_state, list(star.final_states)[0], '')
        star.add_transition(list(a.final_states)[0], list(star.final_states)[0], '')
        star.add_transition(list(a.final_states)[0], a.initial_state, '')
        star.add_transition_dict(a.transitions)
        return star

    def construct_nfa(self):
        language = set()
        previous = "::e::"

        for char in self.regex:

            if char in self.alphabet:
                language.add(char)
                if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket, self.star]):
                    self.add_operator_to_stack(self.dot)
                self.automata.append(self.base_struct(char))

            elif char == self.openingBracket:
                if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket, self.star]):
                    self.add_operator_to_stack(self.dot)
                self.stack.append(char)

            elif char == self.closingBracket:
                if previous in self.operators:
                    raise Exception(f"Error processing '{char}' after '{previous}'")

                while True:
                    if len(self.stack) == 0:
                        raise Exception(f"Error processing '{char}', Empty stack.")
                    o = self.stack.pop()
                    if o == self.openingBracket:
                        break
                    elif o in self.operators:
                        self.process_operator(o)

            elif char == self.star:
                if previous in self.operators or previous == self.openingBracket or previous == self.star:
                    raise Exception(f"Error processing '{char}' after '{previous}'")
                self.process_operator(char)

            elif char in self.operators:
                if previous in self.operators or previous == self.openingBracket:
                    raise Exception(f"Error processing '{char}' after '{previous}'")
                else:
                    self.add_operator_to_stack(char)

            else:
                raise Exception(f"Symbol '{char}' is not allowed")
            previous = char

        while len(self.stack) != 0:
            op = self.stack.pop()
            self.process_operator(op)

        if len(self.automata) > 1:
            print(self.automata)
            raise Exception("Regex could not be parsed successfully")

        self.nfa = self.automata.pop()
        self.nfa.inputs = language

    def add_operator_to_stack(self, operator):
        while True:
            if len(self.stack) == 0:
                break

            top = self.stack[len(self.stack) - 1]

            if top == self.openingBracket:
                break

            if top == operator or top == self.dot:
                op = self.stack.pop()
                self.process_operator(op)

            else:
                break
        self.stack.append(operator)

    def process_operator(self, operator):
        if len(self.automata) == 0:
            raise Exception(f"Error processing operator {operator}. Stack is empty")

        if operator == self.star:
            a = self.automata.pop()
            self.automata.append(self.star_struct(a))

        elif operator in self.operators:
            if len(self.automata) < 2:
                raise Exception(f"Error processing operator '{operator}'. Inadequate operands")

            a = self.automata.pop()
            b = self.automata.pop()

            if operator == self.plus:
                self.automata.append(self.plus_struct(b, a))

            elif operator == self.dot:
                self.automata.append(self.dot_struct(b, a))

    def get_nfa(self):
        # print(self.nfa.initial_state)
        self.nfa.initial_state = {self.nfa.initial_state}
        return self.nfa

    def __str__(self) -> str:
        regex_print = f"""regex={self.regex}
initial_states={self.nfa.initial_state}
transitions={self.nfa.transitions}
final_states={self.nfa.final_states}
states={self.nfa.states}
        """
        return regex_print


def convert_transitions_normal_form(transitions: dict):
    new_transition_dict = dict()
    for key, val in transitions.items():
        new_transition_dict.setdefault(key, dict())
        for _key, _val in val.items():
            new_dict = {list(_val)[0]: _key}
            new_transition_dict.get(key).update(new_dict)

    return new_transition_dict


def reverse_transition(transitions: dict):
    new_transition_dict = dict()
    for key, val in transitions.items():
        new_transition_dict.setdefault(key, dict())
        for _key, _val in val.items():
            new_dict = {_val: _key}
            new_transition_dict.get(key).update(new_dict)

    return new_transition_dict


def convert_to_states_to_normal(self, states, initial_state):
    new_states = set()
    new_final_states = set()

    for state in states:
        new_states.add(str(state))

    initial_state = {str(self.initial_state)}
    for state in self.nfa.final_states:
        new_final_states.add(str(state))

    self.nfa.states = new_states
    self.nfa.final_states = new_final_states
