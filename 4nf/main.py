import sys
from deps import FDep, MVDep, Schema

class FDUtils:
    def __init__(self, fd_filename: str):
        self.f = Schema()
        self.fd_filename = fd_filename

    def init(self):
        self.populate_fds()
        print("Is In 4NF?: ")
        print(self.f.is_in_4nf())

        print("\nDecomposition: ")
        for f in self.f.get_4nf_decomposition():
            print(f)
            print()


    def populate_fds(self):
        has_processed_attributes = False
        for line in open(self.fd_filename, "r"):
            if not has_processed_attributes:
                self.add_attributes([x for x in line.strip()])
                has_processed_attributes = True
            else:
                self.add_dep(line.strip())

    def get_attrs(self, input: str) -> set:
        attrs = set()
        for attr in input:
            attrs.add(attr)

        return attrs

    def add_attributes(self, input: list):
        self.f.add_attributes(input)

    def add_dep(self, input: str):
        if "->>" in input:
            attrs = input.split("->>")
            lhs = self.get_attrs(attrs[0])
            rhs = self.get_attrs(attrs[1])
            self.f.add_mvd(MVDep(lhs, rhs))
        else: 
            attrs = input.split("->")
            lhs = self.get_attrs(attrs[0])
            rhs = self.get_attrs(attrs[1])
            self.f.add_fd(FDep(lhs, rhs))


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <fd_file>")
        return

    utils = FDUtils(sys.argv[1])
    utils.init()


main()
