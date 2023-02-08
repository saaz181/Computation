from typing import Self
import exceptions
from collections import deque

class DFA:
    def __init__(self, states: {}, inputs: {}, transitions: {str: {str: str}}, final_states: {},
                 initial_state: str | set | tuple | frozenset):
        self.states = states
        self.inputs = inputs
        self.transitions = transitions
        self.final_states = final_states
        self.initial_state = initial_state

    def complement(self):
        # we need to just convert final states to normal states and vise versa
        return self.__class__(
            states=self.states,
            inputs=self.inputs,
            transitions=self.transitions,
            final_states=self.states - self.final_states,
            initial_state=self.initial_state
        )

    @staticmethod
    def _construct_new_state_transitions(self_dfa, other_dfa) -> (set, set, dict):
        """ it takes :other_dfa and construct new
            initial_states, transitions and states
            on the same input symbol in both DFAs
        """
        if self_dfa.inputs != other_dfa.inputs:
            raise exceptions.SymbolMisMatchException('The Input Symbols are not Equal!')

        new_initial_state = (self_dfa.initial_state, other_dfa.initial_state)
        new_transitions = {}
        new_states = set()

        queue = deque()
        queue.append(new_initial_state)
        new_states.add(new_initial_state)

        while queue:
            curr_state = queue.popleft()
            curr_state_transition = new_transitions.setdefault(curr_state, dict())

            state_1, state_2 = curr_state
            transition_1 = self_dfa.transitions.get(state_1)
            transition_2 = other_dfa.transitions.get(state_2)

            for c in self_dfa.inputs:
                # result of transition_1 and transition_2 over alphabet(input alphabets)
                res_trans = (transition_1.get(c), transition_2.get(c))
                curr_state_transition[c] = res_trans

                if res_trans not in new_states:
                    new_states.add(res_trans)
                    queue.append(res_trans)

        return new_initial_state, new_states, new_transitions

    def union(self, other_dfa) -> Self:
        """
        param other_dfa: refer to another DFA class
        :return: returns the union of passed DFA with current DFA
        """

        new_initial_state, new_states, new_transitions = self._construct_new_state_transitions(self, other_dfa)

        """
        Due to the book the union of 2 dfa is accepted by new DFA if
        p in final_state_1 or q in final_state_2
        """

        new_final_state = set()
        for (state_1, state_2) in new_states:
            if state_1 in self.final_states or state_2 in other_dfa.final_states:
                new_final_state.add((state_1, state_2))

        return self.__class__(
            states=new_states,
            transitions=new_transitions,
            final_states=new_final_state,
            initial_state=new_initial_state,
            inputs=self.inputs
        )

    @classmethod
    def union(cls, dfa1: Self, dfa2: Self) -> Self:

        new_initial_state, new_states, new_transitions = DFA._construct_new_state_transitions(dfa1, dfa2)

        new_final_state = set()
        for (state_1, state_2) in new_states:
            if state_1 in dfa1.final_states or state_2 in dfa2.final_states:
                new_final_state.add((state_1, state_2))

        return cls(
            states=new_states,
            transitions=new_transitions,
            final_states=new_final_state,
            initial_state=new_initial_state,
            inputs=dfa1.inputs
        )

    def intersection(self, other_dfa: Self) -> Self:

        new_initial_state, new_states, new_transitions = self._construct_new_state_transitions(self, other_dfa)
        new_final_states = set()

        for state_1, state_2 in new_states:
            if state_1 in self.final_states and state_2 in other_dfa.final_states:
                new_final_states.add((state_1, state_2))

        return self.__class__(
            states=new_states,
            transitions=new_transitions,
            final_states=new_final_states,
            initial_state=new_initial_state,
            inputs=self.inputs
        )

    @classmethod
    def intersection(cls, dfa1: Self, dfa2: Self) -> Self:
        new_initial_state, new_states, new_transitions = cls._construct_new_state_transitions(dfa1, dfa2)
        new_final_states = set()

        for state_1, state_2 in new_states:
            if state_1 in dfa1.final_states and state_2 in dfa2.final_states:
                new_final_states.add((state_1, state_2))

        """
        because inputs are dfa1 and dfa2 should be equal
        doesn't make difference to write dfa1.inputs or dfa2.inputs
        """

        return cls(
            states=new_states,
            transitions=new_transitions,
            final_states=new_final_states,
            initial_state=new_initial_state,
            inputs=dfa1.inputs
        )

    def difference(self, other_dfa: Self) -> Self:
        """
        It does the calculation by -> self - other_dfa

        :return: DFA class
        """
        new_initial_state, new_states, new_transitions = self._construct_new_state_transitions(self, other_dfa)
        new_final_states = set()

        for state_1, state_2 in new_states:
            if state_1 in self.final_states and state_2 not in other_dfa.final_states:
                new_final_states.add((state_1, state_2))

        return self.__class__(
            states=new_states,
            transitions=new_transitions,
            final_states=new_final_states,
            initial_state=new_initial_state,
            inputs=self.inputs
        )

    @classmethod
    def difference(cls, dfa1: Self, dfa2: Self) -> Self:
        """
        calculation -> dfa1 - dfa2
        """
        new_initial_state, new_states, new_transitions = cls._construct_new_state_transitions(dfa1, dfa2)
        new_final_states = set()

        for state_1, state_2 in new_states:
            if state_1 in dfa1.final_states and state_2 not in dfa2.final_states:
                new_final_states.add((state_1, state_2))

        """
        because inputs are dfa1 and dfa2 should be equal
        doesn't make difference to write dfa1.inputs or dfa2.inputs
        """

        return cls(
            states=new_states,
            transitions=new_transitions,
            final_states=new_final_states,
            initial_state=new_initial_state,
            inputs=dfa1.inputs
        )

    def is_subset(self, other_dfa: Self) -> bool:
        """
        is self subset of other_dfa
        self - other_dfa = empty -> self is subset of other_dfa else False
        """
        new_initial_state, new_states, new_transitions = self._construct_new_state_transitions(self, other_dfa)
        new_final_states = set()

        for state_1, state_2 in new_states:
            if state_1 in self.final_states and state_2 not in other_dfa.final_states:
                new_final_states.add((state_1, state_2))

        return len(new_final_states) == 0

    @classmethod
    def is_subset(cls, dfa1: Self, dfa2: Self) -> bool:
        """
        dfa1 is subset of dfa2
        dfa1 - dfa2 = 0 then dfa1 is subset of dfa2 otherwise False
        """
        new_initial_state, new_states, new_transitions = cls._construct_new_state_transitions(dfa1, dfa2)
        new_final_states = set()

        for state_1, state_2 in new_states:
            if state_1 in dfa1.final_states and state_2 not in dfa2.final_states:
                new_final_states.add((state_1, state_2))

        return len(new_final_states) == 0

    def is_disjoint(self, other_dfa: Self) -> bool:
        """
        if self.intersection(self, other_dfa).final_states == empty set then 2 language are disjoint
        """
        return len(self.intersection(other_dfa).final_states) == 0

    @classmethod
    def is_disjoint(cls, dfa1: Self, dfa2: Self) -> bool:
        return len(cls.intersection(dfa1, dfa2).final_states) == 0
