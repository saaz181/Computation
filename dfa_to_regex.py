import dfa as dfa_module


class Consts:
    EPSILON = '$'


def split_into_unique(string):
    i, j, brac = 0, 0, 0
    result = []

    for c in string:
        if c == "(":
            brac += 1

        elif c == ")":
            brac -= 1

        if brac == 0:
            if c == "+":
                result.append(string[i:j])
                i = j + 1
        j += 1

    result.append(string[i:j])
    result = list(set(result))

    if "" in result:
        result.remove("")

    return result


def union_regex(reg1, reg2):
    split_reg_1 = split_into_unique(reg1)
    split_reg_2 = split_into_unique(reg2)

    merged_regex = list(set(split_reg_1) | set(split_reg_2))
    return "+".join(merged_regex)


def concat_regex(string_1, string_2):
    if string_1 == "" or string_2 == "":
        return ""

    elif string_1[-1] == Consts.EPSILON:
        return f"{string_1[:-1]}{string_2}"

    elif string_2[0] == Consts.EPSILON:
        return f"{string_1}{string_2[2:]}"

    else:
        return f"{string_1}{string_2}"


def kleene_star_regex(string):
    if string == Consts.EPSILON:
        return Consts.EPSILON

    elif string == "":
        return Consts.EPSILON

    else:
        return f"{bracket(string)}*"


# put a parenthesis around the string
def bracket(string):
    if len(string) <= 1:
        return string
    else:
        return f"({string})"


def is_final(state, visited: list, dfa):
    if state in dfa.final_states:
        return True
    else:
        visited.append(state)
        for alphabet in dfa.inputs:
            next_state = dfa.transitions.get(state).get(alphabet)
            if next_state not in visited:
                if is_final(next_state, visited, dfa):
                    return True
    return False


def dfa_to_regex(dfa):
    L = {}  # converted state to regex

    # find dead states
    is_not_dead = {}

    for state in dfa.compute_reachable_states():
        is_not_dead[state] = is_final(state, [], dfa)

    regex_dfa = dfa_module.DFA(set(), set(), dict(), set(), '')

    # make new start state
    regex_dfa.initial_state = 'P0'

    # make new final states
    regex_dfa.final_states.add('P1')
    regex_dfa.states.add(regex_dfa.initial_state)

    regex_dfa.states = regex_dfa.states.union(dfa.compute_reachable_states())
    regex_dfa.states.add(list(regex_dfa.final_states)[0])
    regex_dfa.inputs = dfa.inputs.union({Consts.EPSILON})

    # attach initial state of regex_dfa to initial state of dfa with epsilon transition
    regex_dfa.add_transition(regex_dfa.initial_state, dfa.initial_state, Consts.EPSILON, input_symbol_first=True)

    # append rest of the transitions of dfa to regex_dfa
    for state in dfa.compute_reachable_states():
        regex_dfa.transitions.setdefault(state, dict())
        for alphabet in dfa.inputs:
            next_state = dfa.transitions.get(state).get(alphabet)
            # appending only those which are not reachable from themselves from

            if is_not_dead[next_state]:
                regex_dfa.add_transition(state, next_state, alphabet, input_symbol_first=True)

    # attach final states of dfs to final state of regex_dfa with epsilon transition
    for state in dfa.final_states:
        regex_dfa.add_transition(state, list(regex_dfa.final_states)[0], Consts.EPSILON, input_symbol_first=True)

    regex_dfa.transitions.setdefault(list(regex_dfa.final_states)[0], dict())

    for state_1 in regex_dfa.states:
        L[state_1] = dict()

        for state_2 in regex_dfa.states:
            L[state_1][state_2] = []

        for alphabet, next_state in regex_dfa.transitions[state_1].items():
            L[state_1][next_state].append(alphabet)

    reachable_non_dead_states = filter(lambda x: is_not_dead[x], dfa.compute_reachable_states())

    # removing states one by one regex_dfa.states:
    for chosen_state in reachable_non_dead_states:

        # for Kleene star
        string = ""
        for transition_string in L[chosen_state][chosen_state]:
            string = union_regex(string, transition_string)

        if string != "":
            string = kleene_star_regex(string)
            L[chosen_state][chosen_state] = [string]

            # for appending star with next values
            next_states = list(regex_dfa.transitions.get(chosen_state).items())

            for alphabet, next_state in next_states:
                del regex_dfa.transitions[chosen_state][alphabet]

                if chosen_state != next_state:
                    for ind in range(len(L[chosen_state][next_state])):
                        L[chosen_state][next_state][ind] = concat_regex(string, L[chosen_state][next_state][ind])
                        regex_dfa.transitions \
                            [chosen_state] \
                            [L[chosen_state][next_state][ind]] = next_state

        # concatenating prev state of chosen state to next states of chosen state
        for prev_state in regex_dfa.states:

            if prev_state != chosen_state:

                prev_next_states = list(regex_dfa.transitions.get(prev_state).items())

                for alphabet, next_state in prev_next_states:

                    if next_state == chosen_state:

                        # connecting prev_state to next of chosen
                        all_new_strings = []

                        for chosen_state_alphabet, chosen_next_state \
                                in regex_dfa.transitions.get(chosen_state).items():

                            new_strings = []

                            for prev_to_chosen in L[prev_state][chosen_state]:
                                chosen_to_next = chosen_state_alphabet

                                # concatenate regex from previous state with curr state elimination
                                string = concat_regex(prev_to_chosen, chosen_to_next)

                                regex_dfa.transitions[prev_state][string] = chosen_next_state

                                new_strings.append(string)
                                all_new_strings.append(string)

                            L[prev_state][chosen_next_state].extend(new_strings)

                        if alphabet not in all_new_strings:
                            del regex_dfa.transitions[prev_state][alphabet]

    # at the end, only transition from initial -> final remains
    # we must combine transition from start to end within the transition alphabet & prev regex

    regex = ""
    for transition_string in L[regex_dfa.initial_state][list(regex_dfa.final_states)[0]]:
        regex = union_regex(regex, transition_string)

    return regex
