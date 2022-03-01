import sys
from fds import FDep, FDSet

class FDUtils:
    def __init__(self, fd_filename: str, command_filename: str, output_filename: str):
        self.f = FDSet()
        self.fd_filename = fd_filename
        self.command_filename = command_filename
        self.output_filename = output_filename

    def init(self):
        self.populate_fds()
        self.process_commands()

    def populate_fds(self):
        has_processed_attributes = False
        for line in open(self.fd_filename, "r"):
            if not has_processed_attributes:
                self.add_attributes(line.strip().split(","))
                has_processed_attributes = True
            else:
                self.add_fd(line.strip())

    def process_commands(self):
        results = []
        for line in open(self.command_filename, "r"):
            command = line.strip()
            results.append((command, getattr(self.f, command)()))

        with open(self.output_filename, "w") as out:
            out.write(str(self.f) + "\n\n")

            for command, result in results:
                out.write(command + "\n")
                if isinstance(result, list):
                    for r in result:
                        out.write(str(r) + "\n")
                else:
                    out.write(str(result) + "\n")

                out.write("\n")

    def get_attrs(self, input: str) -> set:
        attrs = set()
        for attr in input:
            attrs.add(attr)

        return attrs

    def add_attributes(self, input: list):
        self.f.add_attributes(input)

    def add_fd(self, input: str):
        self.f.add_fd(self.get_fd(input))

    def get_fd(self, input: str) -> FDep:
        attrs = input.split("->")
        lhs = self.get_attrs(attrs[0])
        rhs = self.get_attrs(attrs[1])
        return FDep(lhs, rhs)


def main():
    if len(sys.argv) != 4:
        print("Usage: python main.py <fd_file> <commands_file> <output_file>")
        return

    utils = FDUtils(sys.argv[1], sys.argv[2], sys.argv[3])
    utils.init()


main()
