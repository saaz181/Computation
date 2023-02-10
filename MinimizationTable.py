import exceptions
from itertools import combinations

'''
states = {q0, q1, q2, q3, q4, q5}
    [
    [1],                q1 
    [2, 3],             q2
    [4, 5, 6],          q3
    [4, 5 ,6 ,7],       q4
    [8, 9, 10 ,11, 12]  q5
    
    q0, q1, q2, q3, q4
    ]
    
    
   q1| 0
   q2| 0 0
   q3| 0 0 0 
   q4| 0 0 0 0
   q5| 0 0 0 0 0 
 ____________________
     |q0|q1|q2|q3|q4|

'''


class MinimizationTable:
    def __init__(self, states, create_from_table=False, table_data=None):
        self.table = dict()
        self.states = states
        self.table_back_map = {}
        if create_from_table:
            self.table = table_data
        else:
            self._fill_out_table()

    def save_current_table_into_back_map(self):
        self.table_back_map = self.table.copy()

    @staticmethod
    def _make_all_possible_pairs_of_list(data: [], additional_data: [] = None):
        combinations = [[a, b] for idx, a in enumerate(data) for b in data[idx + 1:]]

        if additional_data:
            new_list = []
            for comb in combinations:
                for item in additional_data:
                    new_li = [*comb, item]
                    new_list.append(new_li)
            return new_list

        return combinations

    @staticmethod
    def compare_list_of_sets(list_set_1: list[set | frozenset], list_set_2: list[set | frozenset]) -> bool:
        len1, len2 = len(list_set_1), len(list_set_2)
        if len1 != len2:
            return False
        eq_count = 0

        for element in list_set_1:
            for other in list_set_2:
                if other == element:
                    eq_count += 1

        return eq_count == len1

    def _fill_out_table(self):
        table_pairs = list(combinations(self.states, 2))
        for pair in table_pairs:
            self.table.setdefault(tuple(pair), False)

        return self.table

    def update_table(self, pair: tuple, value=True):
        if pair in self.table.keys():
            self.table.update({pair: value})
            return self.__class__(
                self.states,
                create_from_table=True,
                table_data=self.table
            )

        elif tuple(reversed(pair)) in self.table.keys():
            self.table.update({tuple(reversed(pair)): value})
            return self.__class__(
                self.states,
                create_from_table=True,
                table_data=self.table
            )

        else:
            raise exceptions.ElementNotInTable(f'The "{pair}" Not Found!')

    def keys(self):
        return list(self.table.keys())

    def is_column_available(self, state):
        for pair in self.keys():
            if state in pair:
                return True
        return False

    def is_checked(self, pair: tuple, value=True):
        if pair in self.table.keys():
            return self.table.get(pair) == value

        elif tuple(reversed(pair)) in self.table.keys():
            reverse_pair = tuple(reversed(pair))
            return self.table.get(reverse_pair) == value

        else:
            raise exceptions.ElementNotInTable(f'The "{pair}" Not Found!')

    def convert_table_into_set_objects(self):
        new_list_set = []
        for item in self.table.items():
            pair, value = item
            pair_set = set(pair)
            pair_set.add(value)
            new_list_set.append(pair_set)

        return new_list_set

    def pop(self, pair: tuple):
        if pair in self.table.keys():
            self.table.pop(pair)

        elif tuple(reversed(pair)) in self.table.keys():
            self.table.pop(tuple(reversed(pair)))

        else:
            raise exceptions.ElementNotInTable(f'The "{pair}" Not Found!')

    def remove_item_by_value(self, value=True):
        filtered_list = list(filter(lambda x: x[1] == value, self.table.items()))
        for item in filtered_list:
            pair, val = item
            self.pop(pair)

    def filter_item_by_value(self, value=True, update_table=False):
        filtered_list = filter(lambda x: x[1] == value, self.table.items())
        new_table_dict = {}
        for item in filtered_list:
            pair, value = item
            new_table_dict.setdefault(pair, value)

        if update_table:
            self.table = new_table_dict

        return new_table_dict

    def __eq__(self, other):
        current_table_set = self.convert_table_into_set_objects()
        other_table_set = other.convert_table_into_set_objects()
        return self.compare_list_of_sets(current_table_set, other_table_set)

    def bind_minimized_states(self, remained_state: list, include_original=True) -> list[set]:
        minimized_set_of_states = []
        for index, pair in enumerate(remained_state):
            state_1, state_2 = pair
            minimized_set = set(pair)

            for s_pair in remained_state[index + 1:]:
                if state_1 in s_pair or state_2 in s_pair:
                    minimized_set.add(s_pair[0])
                    minimized_set.add(s_pair[1])
                    remained_state.remove(s_pair)

            self.states -= minimized_set
            # remained_state.remove(pair)

            minimized_set_of_states.append(minimized_set)

        if include_original:
            for state in self.states:
                minimized_set_of_states.append({state})

        return minimized_set_of_states
