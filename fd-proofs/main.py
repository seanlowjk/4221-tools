import sys

from deps import Schema, FDep, MVDep, Rules

def process_dep(dep):
    if "->>" in dep:
        lhs, rhs = dep.split("->>")
        return MVDep(lhs, rhs)
    else: 
        lhs, rhs = dep.split("->")
        return FDep(lhs, rhs)

def parse_rule(io_line: str):
    """
    Parses the io_line to get the following: 

    1. dep (the dependency to be challenged)
    2. rule (the rule to be challenged)
    3. preds (the predicate fds to be challenged)
    """
    inputs = io_line.split(" ")

    if len(inputs) < 2:
        raise Exception("Error In Handling: {}".format(inputs))

    if len(inputs) == 2:
        dep, rule = inputs 
        dep = process_dep(dep)

        return dep, rule, [], ''
    elif len(inputs) == 3:
        dep, rule, preds = inputs 
        dep = process_dep(dep)
        preds = preds.split(',')

        return dep, rule, preds, ''
    else: 
        dep, rule, preds, aug = inputs 
        dep = process_dep(dep)
        preds = preds.split(',')

        return dep, rule, preds, aug

def is_rule_valid(dep, rule, preds, aug, schema):
    if rule == 'Given':
        return True 

    if type(dep) == FDep:
        if rule == 'Reflexivity':
            return Rules.is_reflexitivity_fd(dep)
        elif rule == 'Transitivity':
            if len(preds) != 2:
                raise Exception("Error In Handling: {}".format(dep, rule, preds))
            fd_lhs = schema.get_rule(int(preds[0]))
            fd_rhs = schema.get_rule(int(preds[1]))

            return Rules.is_transitivity_fd(dep, fd_lhs, fd_rhs)
        elif rule == 'Augmentation':
            if len(preds) != 1:
                raise Exception("Error In Handling: {}".format(dep, rule, preds))
            fd_init = schema.get_rule(int(preds[0]))
            return Rules.is_augmentation_fd(dep, fd_init, set(aug))
        elif rule == 'Coalescence':
            if len(preds) != 2:
                raise Exception("Error In Handling: {}".format(dep, rule, preds))
            mvd_init = schema.get_rule(int(preds[0]))
            fd_init = schema.get_rule(int(preds[1]))

            return Rules.is_coalescence_mvd(dep, mvd_init, fd_init)
        else: 
            raise Exception("Error In Handling: {}".format(rule))
    else:
        if rule == 'Complementation':
            if len(preds) != 1:
                raise Exception("Error In Handling: {}".format(dep, rule, preds))
            mvd_init = schema.get_rule(int(preds[0]))
            return Rules.is_complementation_mvd(dep, mvd_init, schema)
        elif rule == 'Augmentation':
            if len(preds) != 1:
                raise Exception("Error In Handling: {}".format(dep, rule, preds))
            mvd_init = schema.get_rule(int(preds[0]))
            return Rules.is_augmentation_mvd(dep, mvd_init, set(aug), schema)
        elif rule == 'Transitivity':
            if len(preds) != 2:
                raise Exception("Error In Handling: {}".format(dep, rule, preds))
            mvd_lhs = schema.get_rule(int(preds[0]))
            mvd_rhs = schema.get_rule(int(preds[1]))

            return Rules.is_transitivity_mvd(dep, mvd_lhs, mvd_rhs)
        elif rule == 'Replication':
            if len(preds) != 1:
                raise Exception("Error In Handling: {}".format(dep, rule, preds))
            fd_init = schema.get_rule(int(preds[0]))
            return Rules.is_replication_mvd(dep, fd_init)
        else: 
            raise Exception("Error In Handling: {}".format(rule))

def print_rule(no, dep, rule, preds, aug):
    preds = [int(pred) for pred in preds]
    if len(preds) == 0 and len(aug) == 0:
        print('{}. {} [ {} ]'.format(no, dep, rule))
        return

    if len(aug)== 0:
        print('{}. {} [ {} {} ]'.format(no, dep, rule, preds))
        return

    print('{}. {} [ {} {} with {} ]'.format(no, dep, rule, preds, aug))

def populate_rules(filename):
    schema = Schema()

    has_processed_attributes = False
    rule_counter = 0
    for line in open(filename, "r"):
        line = line.strip()
        if not has_processed_attributes:
            schema = Schema(line)
            has_processed_attributes = True
        else:
            dep, rule, preds, aug = parse_rule(line)
            if not is_rule_valid(dep, rule, preds, aug, schema):
                print("Invalid Step: {}".format(line))
                return
            else: 
                schema.add_dep(dep)
                rule_counter = rule_counter + 1
                print_rule(rule_counter, dep, rule, preds, aug)

    print('QED')

def main():
    if len(sys.argv) != 2:
        print("Usage python main.py <proof_file>")
        return 

    populate_rules(sys.argv[1])

main()
