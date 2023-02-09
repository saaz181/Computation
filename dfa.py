import networkx as nx
import exceptions
from collections import deque
from typing import Self
from MinimizationTable import MinimizationTable
import Regex
import dfa_to_regex

# https://stackoverflow.com/questions/28237955/same-name-for-classmethod-and-instancemethod
class hybridmethod:
    def __init__(self, fclass, finstance=None, doc=None):
        self.fclass = fclass
        self.finstance = finstance
        self.__doc__ = doc or fclass.__doc__
        # support use on abstract base classes
        self.__isabstractmethod__ = bool(
            getattr(fclass, '__isabstractmethod__', False)
        )

    def classmethod(self, fclass):
        return type(self)(fclass, self.finstance, None)

    def instancemethod(self, finstance):
        return type(self)(self.fclass, finstance, self.__doc__)

    def __get__(self, instance, cls):
        if instance is None or self.finstance is None:
            # either bound to the class, or no instance method available
            return self.fclass.__get__(cls, None)
        return self.finstance.__get__(instance, cls)


class DFA:
    def __init__(self,
                 states: {},
                 inputs: set[str],
                 transitions: {str | int: {str: str | int | frozenset | tuple}},
                 final_states: set | frozenset,
                 initial_state: str | tuple | frozenset | int):
        self.states = states
        self.inputs = inputs
        self.transitions = transitions
        self.final_states = final_states
        self.initial_state = initial_state

    def _get_next_state(self, current_state: str | frozenset, m_input: str):
        if current_state is not None and current_state in self.states:
            if m_input in self.transitions.get(current_state):
                return self.transitions.get(current_state).get(m_input)
        return None

    def _construct_dfa_graph(self):
        G = nx.DiGraph()
        for state in self.states:
            for alphabet in self.inputs:
                target_state = self.transitions.get(state).get(alphabet)
                G.add_edge(state, target_state)

        return G

    def read_inputs(self, input_str):
        pass

    def accept_input(self, input_str):
        current_state = self.initial_state
        for c in input_str:
            current_state = self._get_next_state(current_state, c)

        return current_state in self.final_states

    def compute_reachable_states(self):
        visited_state = {self.initial_state}
        states = [self.initial_state]

        while len(states) > 0:
            try:
                state = states[0]
                states.pop(0)
            except IndexError:
                break

            for next_state in self.transitions.get(state).values():
                if next_state not in visited_state:
                    visited_state.add(next_state)
                    states.append(next_state)

        return visited_state

    def is_empty(self):
        return len(self.compute_reachable_states() & self.final_states) == 0

    def is_finite(self):
        # check that if there is loop or cycle in DFA
        # if there is a loop/cycle the language is infinite otherwise it's finite
        dfa_graph = self._construct_dfa_graph()
        try:
            res = nx.find_cycle(dfa_graph, orientation='original')
            return False
        except nx.NetworkXNoCycle:
            return True

    def __len__(self):
        if self.is_finite() and not self.is_empty():
            maximum_word_length = self.longest_word_length()
            if maximum_word_length:
                smallest_word_length = self.shortest_word_length()
                dfa_graph = self._construct_dfa_graph()
                count = 0
                for word_length in range(smallest_word_length, maximum_word_length + 1):
                    for final_state in self.final_states:
                        paths = nx.all_simple_paths(dfa_graph, self.initial_state, final_state)
                        for path in paths:
                            if len(path) == word_length:
                                count += 1

                return count

            else:
                raise exceptions.InfiniteFiniteException('The DFA Language is finite, but it accepts infinite strings')
        else:
            raise exceptions.InfiniteLanguageException('The Language accepted by DFA is infinite')

    def shortest_word_length(self):
        if self.is_finite():
            dfa_graph = self._construct_dfa_graph()
            shortest_path = []
            for final_state in self.final_states:

                try:
                    path_length = nx.shortest_path_length(dfa_graph, self.initial_state, final_state)
                    shortest_path.append(path_length)

                except nx.NetworkXNoPath:
                    print(f'Path from {self.initial_state} -> {final_state} is not Found!')
                    pass

                except nx.NodeNotFound:
                    print('node are not added properly to graph')
                    pass

            return min(shortest_path)
        return 'The Language is not Finite'

    def longest_word_length(self):
        if self.is_finite():
            dfa_graph = self._construct_dfa_graph()
            longest_path = []
            for final_state in self.final_states:

                try:
                    path_length = nx.dag_longest_path_length(dfa_graph, self.initial_state, final_state)
                    longest_path.append(path_length)

                except nx.NetworkXNoPath:
                    print(f'Path from {self.initial_state} -> {final_state} is not Found!')
                    pass

                except nx.NodeNotFound:
                    print('node are not added properly to graph')
                    pass

            return max(longest_path)

    def minify(self, retain_names=True) -> Self:
        # we use table algorithm to find the minimized DFA (Myhill Nerode Theorem)
        mt = MinimizationTable(self.states)

        while not mt == MinimizationTable(self.states, create_from_table=True, table_data=mt.table_back_map):
            mt.save_current_table_into_back_map()
            for pair in mt.keys():
                state_1, state_2 = pair
                state_1_final = state_1 in self.final_states
                state_2_final = state_2 in self.final_states

                if state_1_final ^ state_2_final:
                    mt.update_table(pair)
                    continue

                for symbol in self.inputs:
                    try:
                        tr_state_1, tr_state_2 = self.transitions.get(state_1).get(symbol), \
                                                 self.transitions.get(state_2).get(symbol)

                        if mt.is_checked((tr_state_1, tr_state_2), value=True):
                            mt.update_table((state_1, state_2), value=True)

                    except exceptions.ElementNotInTable:
                        pass

        filtered_data = mt.filter_item_by_value(value=False)
        minimized_states = mt.bind_minimized_states(list(filtered_data.keys()))

        new_transitions = dict()
        new_states = set()
        new_initial_state = frozenset(self._search_in_list_of_sets(list(minimized_states), self.initial_state))
        new_final_states = set()

        for state_set in minimized_states:
            new_transitions.setdefault(frozenset(state_set), dict())
            new_states.add(frozenset(state_set))
            for symbol in self.inputs:
                # we only need to check the transition of first element, other of the same set are the same
                input_state = list(state_set)[0]
                res_tr = self.transitions.get(input_state).get(symbol)
                # the set that transition of 'input_state' with input symbol transit into
                symbol_value = self._search_in_list_of_sets(list(minimized_states), res_tr)

                # determine the final state(s)
                for f_state in self.final_states:
                    if f_state in symbol_value:
                        new_final_states.add(frozenset(symbol_value))

                new_transitions.get(frozenset(state_set)).setdefault(symbol, frozenset(symbol_value))

        if retain_names:
            return self.__class__(
                states=new_states,
                inputs=self.inputs,
                transitions=new_transitions,
                final_states=new_final_states,
                initial_state=new_initial_state
            )
        # retain_names == False should be implemented

    @staticmethod
    def _search_in_list_of_sets(list_obj: [set], data_to_check):
        for i, set_obj in enumerate(list_obj):
            if {data_to_check}.issubset(set_obj):
                return set_obj
        return False

    @classmethod
    def from_nfa(cls, nfa_instance, minify=True) -> Self:
        # base on algo here: https://www.javatpoint.com/automata-conversion-from-nfa-to-dfa

        new_transition, new_final_states = nfa_instance.eliminate_lambda_closures(update_origin=True)

        q = set()  # set of states
        checked_state = set()  # set of checked state

        for state in nfa_instance.states:
            q.add(frozenset({state}))
        dfa_transitions = dict()

        while not MinimizationTable.compare_list_of_sets(list(checked_state), list(q)):
            for state in list(q):

                dfa_transitions.setdefault(state, dict())
                for input_symbol in nfa_instance.inputs:

                    if state not in checked_state:
                        next_state = nfa_instance.get_next_state(state, input_symbol)
                        dfa_transitions.get(state).setdefault(input_symbol, frozenset(next_state))

                        if next_state not in q:
                            q.add(frozenset(next_state))

                checked_state.add(frozenset(state))

        # determine final states & initial state
        dfa_final_states = set()
        dfa_initial_state = None

        for state in dfa_transitions:
            if len(new_final_states.intersection(state)) > 0:
                dfa_final_states.add(state)

            if len(nfa_instance.initial_state.intersection(state)) > 0:
                dfa_initial_state = state

        if minify:
            cls(
                states=q,
                final_states=dfa_final_states,
                transitions=dfa_transitions,
                initial_state=dfa_initial_state,
                inputs=nfa_instance.inputs
            ).minify()

        return cls(
            states=q,
            final_states=dfa_final_states,
            transitions=dfa_transitions,
            initial_state=dfa_initial_state,
            inputs=nfa_instance.inputs
        )

    def add_transition(self, from_state, to_state, input_symbol, input_symbol_first=False):
        if input_symbol_first:
            if from_state in self.transitions:
                self.transitions.get(from_state).setdefault(input_symbol, to_state)

            else:
                self.transitions.setdefault(from_state, {input_symbol: to_state})

        else:
            # this method specially use for converting regex to dfa
            if isinstance(input_symbol, str):
                input_symbol = set([input_symbol])

            self.states.add(from_state)
            self.states.add(to_state)

            if from_state in self.transitions:
                if to_state in self.transitions[from_state]:
                    self.transitions[from_state][to_state] = self.transitions[from_state][to_state].union(input_symbol)
                else:
                    self.transitions[from_state][to_state] = input_symbol
            else:
                self.transitions.setdefault(from_state, {to_state: input_symbol})

    @classmethod
    def from_regex(cls, regex: str) -> Self:
        compiled_nfa = Regex.Regex(regex)
        return compiled_nfa.nfa.nfa_to_dfa()

    @staticmethod
    def to_regex(dfa):
        regex = dfa_to_regex.dfa_to_regex(dfa)
        return regex


if __name__ == '__main__':
    pass