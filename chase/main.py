import sys

from chase import Schema, FDep, MVDep

def process_dep(dep):
    if "->>" in dep:
        lhs, rhs = dep.split("->>")
        return MVDep(lhs, rhs)
    else: 
        lhs, rhs = dep.split("->")
        return FDep(lhs, rhs)

def process_lossless(line):
    return line.split(' ')

def populate_schema(filename):
    schema = Schema()

    has_processed_attributes = False
    will_process_result = 0
    for line in open(filename, "r"):
        line = line.strip()
        if not has_processed_attributes:
            schema.attributes = sorted(set(line))
            has_processed_attributes = True
        elif will_process_result == 1:
            dep = process_dep(line)
            schema.target = dep
        elif will_process_result == 2:
            schema.proc(process_lossless(line))
            schema.target = MVDep(set(), set())
        else:
            if line != 'RESULT' and line != 'DISTINGUISHED':
                dep = process_dep(line)
                schema.add_dep(dep)
            elif line == 'RESULT': 
                will_process_result = 1 
            else:
                will_process_result = 2
    
    return schema


def main():
    if len(sys.argv) != 2:
        print("Usage python main.py <proof_file>")
        return 

    schema = populate_schema(sys.argv[1])
    schema.init()
    schema.chase()

main()
