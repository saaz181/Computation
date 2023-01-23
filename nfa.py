class NFA:
    def __init__(self, states, transitions: dict, inputs: set, initial_state, final_states):
        self.states = states
        self.transitions = transitions
        self.inputs = inputs
        self.initial_state = initial_state
        self.final_states = final_states

    def _compute_initial_lambda_closures(self):
        lambda_transition_dict = {}

        for state in self.states:
            set_of_lambda_closure = set()
            final_lambda_closure = [state]
            while set_of_lambda_closure != set(final_lambda_closure):
                if len(set_of_lambda_closure) != 0:
                    final_lambda_closure = list(set_of_lambda_closure)

                for lambda_state in final_lambda_closure:
                    lambda_tr_state = self.transitions.get(lambda_state).get('')
                    if lambda_tr_state is not None:
                        set_of_lambda_closure.add(lambda_tr_state)
                    else:
                        set_of_lambda_closure.add(state)

            lambda_transition_dict.setdefault(state, set_of_lambda_closure)

        return lambda_transition_dict

    def get_next_state(self, states, input_symbol, frozen_set=False):
        transition_set = set()

        for state in states:
            if type(state) != str:
                tr_state = self.transitions.get(*state)
            else:
                tr_state = self.transitions.get(state)

            tr_state_transition = tr_state.get(input_symbol)

            for res_state in list(tr_state_transition):
                transition_set.add(res_state)

        return frozenset(transition_set)

    def _compute_lambda_closure(self, states: set):
        # base on algorithm in chapter 3 of Introduction to computation theory page 102
        t = states
        v = set()

        while t != v:
            v = t
            for state in list(states):
                if self.transitions.get(state) is not None:
                    l_tr_state = self.transitions.get(state).get('')
                    if l_tr_state is not None and l_tr_state not in t:
                        t.add(l_tr_state)
                    else:
                        t.add(state)
        return t

    def _compute_sigma_star(self, state, input_symbol):
        initial_set = self._compute_lambda_closure({state})
        next_lambda_closure = set()
        for _state in list(initial_set):
            l_tr_state = self.transitions.get(_state).get(input_symbol)
            if l_tr_state is not None:
                next_lambda_closure.add(frozenset(l_tr_state))

        result = self._compute_lambda_closure(next_lambda_closure)
        return list(result)[0]

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
                if l_tr_state is not None:
                    new_transition.get(state).setdefault(char, l_tr_state)

                else:
                    new_transition.get(state).setdefault(char, l_tr_state)

        if update_origin:
            self.transitions = new_transition
            self.final_states = new_final_states

        return new_transition, new_final_states


nfa = NFA(states={'q0', 'q1', 'q2'},
          inputs={'0', '1'},
          transitions={
              'q0': {'0': {'q0'}, '1': {'q1'}},
              'q1': {'0': {'q1', 'q2'}, '1': {'q1'}},
              'q2': {'0': {'q2'}, '1': {'q1', 'q2'}}
          },
          initial_state={'q0'},
          final_states={'q2'})

# res = nfa.get_next_state({'q1', 'q2'}, '0')
