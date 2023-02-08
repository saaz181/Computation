from dfa import DFA
import Regex


class NFA:
    def __init__(self, states, transitions: dict, inputs: set, initial_state, final_states):
        self.states = states
        self.transitions = transitions
        self.inputs = inputs
        self.initial_state = initial_state
        self.final_states = final_states

    def get_next_state(self, states, input_symbol, frozen_set=False):
        transition_set = set()
        for state in states:
            if type(state) == set or type(state) == list or type(state) == frozenset:
                tr_state = self.transitions.get(*state)
            else:
                tr_state = self.transitions.get(state)

            tr_state_transition = tr_state.get(input_symbol)
            if tr_state_transition is not None:
                for res_state in list(tr_state_transition):
                    transition_set.add(res_state)

        return frozenset(transition_set)

    def get_transitions(self, state, key):
        if isinstance(state, int):
            state = [state]

        tr_states = set()
        for st in state:
            if st in self.transitions:
                for tns in self.transitions[st]:
                    if key in self.transitions[st][tns]:
                        tr_states.add(tns)
        return tr_states

    def _compute_lambda_closure(self, states: set, lambda_frozen=False):
        # base on algorithm in chapter 3 of Introduction to computation theory page 102
        """

        t = {1, 2, 3}
        """
        t = states

        if not isinstance(states, set):
            t = {states}

        found_closure = False
        v = 0

        while not found_closure:
            v = len(t)
            for state in list(t):
                if self.transitions.get(state) is not None:
                    if lambda_frozen:
                        l_tr_state = self.transitions.get(state).get(frozenset({''}))
                    else:
                        l_tr_state = self.transitions.get(state).get('')

                    if l_tr_state is not None and l_tr_state not in t:
                        if type(l_tr_state) == frozenset or type(l_tr_state) == set:
                            for _state in l_tr_state:
                                t.add(_state)
                        else:
                            t.add(l_tr_state)
                    else:
                        t.add(state)

            if v == len(t):
                found_closure = True

        return t

    def _compute_sigma_star(self, states, input_symbol):
        # initial_set = self._compute_lambda_closure(state)

        if type(states) != set and type(states) != frozenset:
            states = {states}
        next_lambda_closure = set()

        for _state in list(states):
            if self.transitions.get(_state) is not None:
                l_tr_state = self.transitions.get(_state).get(input_symbol)

                if l_tr_state is not None:
                    next_lambda_closure.add(frozenset(l_tr_state))

        result = self._compute_lambda_closure(next_lambda_closure)
        if len(result) > 0:
            return list(result)[0]
        return frozenset(result)

    def eliminate_lambda_closures(self, update_origin=False):
        new_transition = dict()
        new_final_states = set()

        for state in self.states:
            new_transition.setdefault(state, dict())

            for f_state in self.final_states:
                if f_state in self._compute_lambda_closure({state}):
                    new_final_states.add(state)

            for char in self.inputs:
                l_tr_state = self._compute_sigma_star(state, char)

                if type(l_tr_state) == set or type(l_tr_state) == frozenset:
                    if len(l_tr_state) > 0:
                        new_transition.get(state).setdefault(char, l_tr_state)

                elif l_tr_state is not None:
                    new_transition.get(state).setdefault(char, l_tr_state)

        if update_origin:
            self.transitions = new_transition
            self.final_states = new_final_states

        return new_transition, new_final_states

    def getEClose(self, _state):
        all_states = set()
        states = set([_state])
        while len(states) != 0:
            state = states.pop()
            all_states.add(state)
            if state in self.transitions:
                for tns in self.transitions[state]:
                    if '' in self.transitions[state][tns] and tns not in all_states:
                        states.add(tns)
        return all_states

    def nfa_to_dfa(self) -> DFA:
        # https://www.javatpoint.com/automata-conversion-from-nfa-with-null-to-dfa

        all_states = dict()
        eclose = dict()
        count = 1
        state1 = self._compute_lambda_closure(self.initial_state)
        eclose[self.initial_state] = state1
        dfa = DFA(set(), self.inputs, dict(), set(), set())
        dfa.initial_state = count
        states = [[state1, count]]
        all_states[count] = state1
        count += 1

        while len(states) != 0:
            [state, from_index] = states.pop()

            for char in dfa.inputs:

                # sigma prime value = tr_state
                tr_state: set = self.get_transitions(state, char)

                # get lambda closure of every state in tr_state
                for s in list(tr_state)[:]:
                    if s not in eclose:
                        eclose[s] = self.getEClose(s)
                    tr_state = tr_state.union(eclose[s])

                if len(tr_state) != 0:
                    if tr_state not in all_states.values():
                        states.append([tr_state, count])
                        all_states[count] = tr_state
                        to_index = count
                        count += 1

                    else:
                        for key, val in all_states.items():
                            if val == tr_state:
                                to_index = key

                    dfa.add_transition(from_index, to_index, char)

        # set final states
        for value, state in all_states.items():
            if list(self.final_states)[0] in state:
                dfa.final_states.add(value)

        dfa.transitions = Regex.convert_transitions_normal_form(dfa.transitions)
        return dfa

    def add_transition(self, state_1: set | frozenset | int, state_2: set | frozenset | int, input_symbol: str):
        if isinstance(input_symbol, str):
            input_symbol = set([input_symbol])

        self.states.add(state_1)
        self.states.add(state_2)
        if state_1 in self.transitions:
            if state_2 in self.transitions[state_1]:
                self.transitions[state_1][state_2] = self.transitions[state_1][state_2].union(input_symbol)
            else:
                self.transitions[state_1][state_2] = input_symbol
        else:
            self.transitions[state_1] = {state_2: input_symbol}

    def add_transition_dict(self, transitions: dict):
        for from_state, to_states in transitions.items():
            for state in to_states:
                self.add_transition(from_state, state, to_states[state])

    def build_from_number(self, start_num):
        translations = dict()
        for i in list(self.states):
            translations[i] = start_num
            start_num += 1

        rebuild = NFA(set(), dict(), self.inputs, set(), set())
        rebuild.initial_state = translations.get(self.initial_state)
        rebuild.final_states.add(translations[list(self.final_states)[0]])
        for from_state, to_states in self.transitions.items():
            for state in to_states:
                if isinstance(state, set) and len(state) > 0:
                    state = list(state)[0]

                rebuild.add_transition(translations[from_state], translations[state], to_states[state])
        return [rebuild, start_num]
