import copy
import time

start_time = time.clock()

def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
    cls.__str__ = __str__
    return cls


@auto_str
class Applicant:
    def __init__(self, gender, age, hasPets, hasMedicalCondition, hasCar, hasDriversL, days):
        self.gender = gender
        self.age = age
        self.hasPets = hasPets
        self.hasMedicalCondition = hasMedicalCondition
        self.hasCar = hasCar
        self.hasDriversL = hasDriversL
        self.days = days


class State:
    def __init__(self, applicant_id, children, spaces_spla, spaces_lahsa):
        self.a_id = applicant_id
        self.children = children
        self.spaces_spla = spaces_spla
        self.spaces_lahsa = spaces_lahsa
        self.best_child = None
        self.is_terminal = False

    # gets children by removing the current state's id
    def get_children(self):
        children_states = []

        for child_id in self.children:
            new_state = copy.deepcopy(self)
            new_state.children.remove(child_id)
            new_state.a_id = child_id

            children_states.append(new_state)

        return children_states


def parse_applicant_detail(detail):
    gender = detail[0]
    age = int(detail[1:4])
    hasPets = detail[4]
    hasMedicalCondition = detail[5]
    hasCar = detail[6]
    hasDriversL = detail[7]
    days = detail[8:]

    return Applicant(gender, age, hasPets, hasMedicalCondition, hasCar, hasDriversL, days)


def spla_allowed(applicant):
    if applicant.hasCar == "Y" and applicant.hasDriversL == "Y" and applicant.hasMedicalCondition == "N":
        return True
    else:
        return False


def lahsa_allowed(applicant):
    if applicant.age > 17 and applicant.gender == "F" and applicant.hasPets == "N":
        return True
    else:
        return False


def chooseState(state, player):
    days = applicants[state.a_id].days
    for i in range(len(days)):
        if player == 0:
            state.spaces_spla[i] += int(days[i])
        elif player == 1:
            state.spaces_lahsa[i] += int(days[i])


def play_spla(state):
    chooseState(state, 0)

    if time.clock() - start_time > 170:
        return evaluate_spla(state)

    if not is_under_limit(state.spaces_spla, spaces_limit_spla):
        return 0

    children_states = state.get_children()

    if len(children_states) == 0:
        return evaluate_spla(state)

    best_score = float('-inf')
    best_child = None

    # lahsa chooses the applicant which satisfies the constraint and gives max score
    for child_state in children_states:
        score = evaluate_lahsa(child_state)

        l_spaces = state.spaces_lahsa[:]
        days = applicants[child_state.a_id].days
        for i in range(len(days)):
            l_spaces[i] += int(days[i])

        if score > best_score and is_under_limit(l_spaces, spaces_limit_lahsa):
            best_child = child_state
            best_score = score

    # if lahsa cannot choose anymore, then spla starts choosing the remaining applicants
    if best_child is None:

        for child_state in children_states:
            s_spaces = state.spaces_spla[:]
            days = applicants[child_state.a_id].days
            for i in range(len(days)):
                s_spaces[i] += int(days[i])

            if is_under_limit(s_spaces, spaces_limit_spla):
                state.spaces_spla = s_spaces

        return evaluate_spla(state)

    return play_lahsa(best_child)


def play_lahsa(state):
    if state is None:
        return 0

    chooseState(state, 1)

    if time.clock() - start_time > 170:
        return evaluate_spla(state)

    if not is_under_limit(state.spaces_lahsa, spaces_limit_lahsa):
        return evaluate_spla(state)

    children_states = state.get_children()

    if len(children_states) == 0:
        return evaluate_spla(state)

    best_score = float('-inf')

    for child_state in children_states:
        score = play_spla(child_state)

        if score > best_score:
            best_score = score

    return best_score


def evaluate_lahsa(state):
    num_spaces = 0

    for day_spaces in state.spaces_lahsa:
        num_spaces += day_spaces

    return num_spaces


def evaluate_spla(state):
    num_spaces = 0

    for day_spaces in state.spaces_spla:
        num_spaces += day_spaces

    return num_spaces


def get_num_days(days):
    num_days = 0
    for i in range(len(days)):
        num_days += int(days[i])

    return num_days


def is_under_limit(days, limit):
    for day in days:
        if day > limit:
            return False
    return True


if __name__ == "__main__":
    spaces_limit_lahsa = -1
    spaces_limit_spla = -1

    num_chosen_lahsa = -1
    num_chosen_spla = -1

    chosen_lahsa_ids = []
    chosen_spla_ids = []

    lahsa_allowed_ids = set()
    spla_allowed_ids = set()

    applicants = {}

    with open('input2.txt') as inputFile:
        spaces_limit_lahsa = int(inputFile.readline().rstrip())
        spaces_limit_spla = int(inputFile.readline().rstrip())

        num_chosen_lahsa = int(inputFile.readline().rstrip())

        for i in range(num_chosen_lahsa):
            chosen_lahsa_ids.append(int(inputFile.readline().rstrip()))

        num_chosen_spla = int(inputFile.readline().rstrip())

        for i in range(num_chosen_spla):
            chosen_spla_ids.append(int(inputFile.readline().rstrip()))

        total_applicants = int(inputFile.readline().rstrip())

        chosen_ids = set(chosen_spla_ids + chosen_lahsa_ids)
        for i in range(total_applicants):
            applicant_detail_str = inputFile.readline().rstrip()
            a_id = int(applicant_detail_str[:5])
            applicants[a_id] = parse_applicant_detail(applicant_detail_str[5:])

            if a_id not in chosen_ids and spla_allowed(applicants[a_id]):
                spla_allowed_ids.add(a_id)
            if a_id not in chosen_ids and lahsa_allowed(applicants[a_id]):
                lahsa_allowed_ids.add(a_id)

    spla_lahsa_intersection = spla_allowed_ids.intersection(lahsa_allowed_ids)

    max_num_days = 0
    max_id = -1

    spla_spaces_filled = [0, 0, 0, 0, 0, 0, 0]
    for a_id in chosen_spla_ids:
        days = applicants[a_id].days
        for i in range(len(days)):
            spla_spaces_filled[i] = int(days[i])

    lahsa_spaces_filled = [0, 0, 0, 0, 0, 0, 0]
    for a_id in chosen_lahsa_ids:
        days = applicants[a_id].days
        for i in range(len(days)):
            lahsa_spaces_filled[i] = int(days[i])

    initial_states = []

    for id in spla_lahsa_intersection:
        spaces_filled = spla_spaces_filled[:]
        days = applicants[id].days
        for i in range(len(days)):
            spaces_filled[i] += int(days[i])

        if is_under_limit(spaces_filled, spaces_limit_spla):
            initial_states.append(State(id, list(spla_lahsa_intersection - {id}), spla_spaces_filled[:], lahsa_spaces_filled[:]))

    best_score = float('-inf')
    best_move = None

    # if spaces_limit_spla == 1:
    #     for id in spla_allowed_ids:
    #         if best_score < get_num_days(applicants[id].days):
    #             best_score = get_num_days(applicants[id].days)
    #             best_move = id
    # else:
    # initial_states.sort(key=lambda x: evaluate_spla(x), reverse=True)
    for state in initial_states:
        score = play_spla(state)

        if score > best_score or time.clock() - start_time > 170:
            best_score = score
            best_move = state.a_id

    with open('output.txt', 'w') as outputFile:
        if best_move is not None:
            print "%05d" % (best_move,)
            print "score : %d" % best_score
            print time.clock() - start_time, "seconds"
            outputFile.write("%05d" % (best_move,))
        else:
            outputFile.write()
