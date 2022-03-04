from itertools import combinations

class AttrComparator:
    """
    A class used to order sets of attributes.
    """

    def compare_attrs_lt(set1: set, set2: set):
        """
        Compares two attribute sets and checks if
        set1 < set2 or not.
        """
        set1, set2 = sorted(set1), sorted(set2)
        if set1 == set2:
            return False

        if len(set1) > len(set2):
            return False

        # If one set is smaller than the other using the
        # native __lt__ method for sets, or the length
        # of one set is smaller than the other.
        if set1 < set2 or len(set1) < len(set2):
            return True

        for i in range(0, len(set1)):
            # If an attribute is lexographically smaller,
            # return True.
            if set1[i] < set2[i]:
                return True

            if set1[i] > set2[i]:
                return False

        return False

class FDep:
    """
    A class used to represent a functional dependency.

    ...

    Attributes
    ----------
    lhs : set
        The set of left-hand side attributes
    rhs : set
        The set of right-hand side attributes
    """

    def __init__(self, lhs, rhs):
        self.lhs = set(lhs)
        self.rhs = set(rhs)

    def __repr__(self):
        return str(self.to_result())

    def __hash__(self):
        """
        Uses the hash values of the LHS and RHS attributes
        to return a new hash value.
        """
        return hash(hash(tuple(self.lhs)) * hash(tuple(self.rhs)))

    def __eq__(self, other):
        """
        Checks if the FDep is equal to another FDep or not.
        """
        if not isinstance(other, FDep):
            return False

        return self.lhs == other.lhs and self.rhs == other.rhs

    def __lt__(self, other):
        # Returns true if self.lhs < other.lhs OR
        # (self.lhs == other.lhs AND self.rhs < other.rhs)
        return AttrComparator.compare_attrs_lt(self.lhs, other.lhs) or (
            sorted(self.lhs) == sorted(other.lhs)
            and AttrComparator.compare_attrs_lt(self.rhs, other.rhs)
        )

    def to_result(self):
        """
        Returns the FDep as the form of [LHS, RHS]
        as required by the assignment.
        """
        return "{} -> {}".format(''.join(sorted(self.lhs)), ''.join(sorted(self.rhs)))

    def is_trivial(self):
        """
        Checks if the FDep is trivial or not.
        """
        return self.lhs == self.rhs or (self.rhs).issubset(self.lhs)

class AttributeClosure(FDep):
    """
    A class used to represent a closure of an attribute set.

    Represented in the form of { attributes -> closure }
    """

    def attributes(self):
        return self.lhs

    def closure(self):
        return self.rhs

    def __eq__(self, other):
        """
        Checks if the AttributeClosure is equal to another AttributeClosure or not.
        """
        if not isinstance(other, AttributeClosure):
            return False

        return self.lhs == other.lhs and self.rhs == other.rhs


class MVDep:
    """
    A class used to represent a mutli-valued dependency.

    ...

    Attributes
    ----------
    lhs : set
        The set of left-hand side attributes
    rhs : set
        The set of right-hand side attributes
    """

    def __init__(self, lhs, rhs):
        self.lhs = set(lhs)
        self.rhs = set(rhs)

    def __repr__(self):
        return str(self.to_result())

    def __hash__(self):
        """
        Uses the hash values of the LHS and RHS attributes
        to return a new hash value.
        """
        return hash(hash(tuple(self.lhs)) * hash(tuple(self.rhs)))

    def __eq__(self, other):
        """
        Checks if the FDep is equal to another FDep or not.
        """
        if not isinstance(other, FDep):
            return False

        return self.lhs == other.lhs and self.rhs == other.rhs

    def __lt__(self, other):
        # Returns true if self.lhs < other.lhs OR
        # (self.lhs == other.lhs AND self.rhs < other.rhs)
        return AttrComparator.compare_attrs_lt(self.lhs, other.lhs) or (
            sorted(self.lhs) == sorted(other.lhs)
            and AttrComparator.compare_attrs_lt(self.rhs, other.rhs)
        )

    def to_result(self):
        """
        Returns the FDep as the form of [LHS, RHS]
        as required by the assignment.
        """
        return "{} ->> {}".format(''.join(sorted(self.lhs)), ''.join(sorted(self.rhs)))


class Schema: 
    """
    A class used to represent a schema.
    ...

    Attributes
    ----------
    attributes : set
        The set of attributes in the schema
    rule_set : RuleSet
        The list of rules.
    """

    def __init__(self, attributes='', fds=[], mvds=[]):
        self.attributes = set(attributes)
        self.fds = fds
        self.mvds = mvds

    def __repr__(self):
        return f"R{sorted(self.attributes)}\nF{sorted(self.fds)}\nM{sorted(self.mvds)}"

    def __str__(self):
        return f"R{sorted(self.attributes)}\nF{sorted(self.fds)}\nM{sorted(self.mvds)}"

    def add_attributes(self, attributes: list):
        """
        Appends attributes to the database instance.
        """
        self.attributes = self.attributes.union(set(attributes))

    def add_fd(self, fd: FDep) -> None:
        """
        Appends fds to the database instance.
        """
        # Prevent adding of FDep if the LHS is empty.
        if len(fd.lhs) == 0:
            return

        fds_to_add = []
        for a in fd.rhs:
            fds_to_add.append(FDep(fd.lhs, set(a)))

        for fd in fds_to_add:
            # Prevent adding of duplicate FDs, when deemed necessary
            if not fd in self.fds:
                self.fds.append(fd)

    def add_mvd(self, mvd: MVDep) -> None:
        """
        Appends mvds to the database instance.
        """
        self.mvds.append(mvd)

    def get_attribute_closure(self, attr) -> AttributeClosure:
        """
        Gets the attribute closure of a set of attributes.
        """
        attr_copy = set(attr).copy()
        fds_copy = self.fds.copy()
        fds_left = set()

        while fds_left != fds_copy:  # Whilte an FDep has been deleted.
            fds_left = fds_copy.copy()
            for f in fds_copy:
                if (f.lhs).issubset(attr_copy):
                    attr_copy = attr_copy.union(f.rhs)
                    fds_copy.remove(f)
                    break

        return AttributeClosure(attr, attr_copy)

    def get_attribute_closures(self) -> list:
        """
        Gets the closure of all subsets of attributes.
        """
        attr_closures = []
        for num_attr in range(1, len(self.attributes) + 1):
            for attrs in combinations(self.attributes, num_attr):
                attrs_copy = set(attrs).copy()
                attr_clos = self.get_attribute_closure(attrs_copy)
                attr_closures.append(attr_clos)

        # Sort the closures for readaibility purposes.
        return sorted(attr_closures)

    def get_essential_attr_closures(self) -> list:
        """
        Gets the closure of all subsets of attributes
        excluding super keys that are not candidate keys.
        """
        attr_closures = []
        all_attribute_closures = self.get_attribute_closures()

        superkeys = self.get_superkeys()
        candidate_keys = self.get_candidate_keys()

        for closure in all_attribute_closures:
            attrs = sorted(closure.attributes().copy())
            if not (attrs in superkeys and not attrs in candidate_keys):
                attr_closures.append(closure)

        # Sort the closures for readaibility purposes.
        return sorted(attr_closures)

    def get_superkeys(self) -> list:
        """
        Gets all the superkeys of the database instance.
        """
        superkeys = []

        for num_attr in range(1, len(self.attributes) + 1):
            for attrs in combinations(self.attributes, num_attr):
                attrs_copy = set(attrs).copy()

                # If the closure of the set of attributes is the same
                # as the set of attributes in the database instance,
                # this set of attributes must be a superkey.
                if self.get_attribute_closure(attrs_copy).closure() == self.attributes:
                    superkeys.append(sorted(attrs_copy))

        # Sort the superkeys for readaibility purposes.
        return sorted(superkeys)

    def get_fd_closure(self) -> list:
        """
        Returns Sigma+, also known as the FDep closure
        of the database instance.
        """
        fd_closure = []

        for num_attr in range(1, len(self.attributes) + 1):
            for attrs in combinations(self.attributes, num_attr):
                attr_closure = self.get_attribute_closure(set(attrs))

                for attr in attr_closure.closure():
                    attr_set = set(attr)

                    # If the FDep is not trivial, then add it in.
                    if not attr_set.issubset(set(attrs)):
                        fd_closure.append(FDep(set(attrs), attr_set))

        # Sort the FDep closure for readaibility purposes.
        return sorted(fd_closure)

    def init_child_schema(self, new_attrs):
        new_fds = []
        new_mvds = []

        for fd in self.get_fd_closure():
            if fd.lhs <= new_attrs and fd.rhs <= new_attrs:
                new_fds.append(fd)

        for mvd in self.mvds:
            if mvd.lhs <= new_attrs and mvd.rhs <= new_attrs:
                new_mvds.append(mvd)

        return Schema(sorted(new_attrs), new_fds, new_mvds)

    def is_in_4nf(self): 
        if len(self.attributes) <= 2:
            return True 

        superkeys = self.get_superkeys()

        for mvd in self.mvds: 
            if not mvd.lhs < mvd.rhs and \
                not mvd.rhs == self.attributes.difference(mvd.lhs) and \
                not sorted(mvd.lhs) in superkeys: 
                return False 
        
        return True 

    def get_4nf_decomposition(self):
        if self.is_in_4nf():
            return [self]

        superkeys = self.get_superkeys()

        for mvd in self.mvds: 
            if not mvd.lhs < mvd.rhs and \
                not mvd.rhs == self.attributes.difference(mvd.lhs) and \
                not sorted(mvd.lhs) in superkeys:
                r1 = mvd.lhs.union(mvd.rhs)
                r2 = self.attributes.difference(mvd.rhs.difference(mvd.lhs))
                R1 = self.init_child_schema(r1)
                R2 = self.init_child_schema(r2)

                return R1.get_4nf_decomposition() + R2.get_4nf_decomposition()


