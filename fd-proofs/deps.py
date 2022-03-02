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

class RuleSet:
    """
    A class used to hold all the derived dependencies 
    from a set of proofs.

    Attributes
    ----------
    deps : list
        The list of attributes in the schema
    """
    def __init__(self):
        self.deps = []

    def add_dep(self, dep):
        self.deps.append(dep)

    def get_dep(self, i: int):
        return self.deps[i - 1]

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

    def __init__(self, attributes=''):
        self.attributes = set(attributes)
        self.rule_set = RuleSet()

    def add_dep(self, rule):
        self.rule_set.add_dep(rule)

    def get_rule(self, i: int):
        return self.rule_set.get_dep(i)

class Rules:
    """
    A helper class used to determine the legality of 
    the rules applied for functional and 
    multi-valued dependencies.
    """
    # FD Rules
    def is_reflexitivity_fd(fd): 
        return type(fd) == FDep and fd.rhs <= fd.lhs

    def is_transitivity_fd(fd, fd_lhs, fd_rhs): 
        return type(fd) == FDep and type(fd_lhs) == FDep and type(fd_rhs) == FDep \
            and fd.lhs == fd_lhs.lhs and fd.rhs == fd_rhs.rhs \
            and fd_lhs.rhs == fd_rhs.lhs 

    def is_augmentation_fd(fd, fd_init, attributes: set):
        return type(fd) == FDep and type(fd_init) == FDep \
            and fd.lhs == fd_init.lhs.union(attributes) \
            and fd.rhs == fd_init.rhs.union(attributes)

    # MVD Ryles 
    def is_complementation_mvd(mvd, mvd_init, schema: Schema):
        return type(mvd) == MVDep and type(mvd_init) == MVDep \
            and mvd.lhs == mvd_init.lhs \
            and mvd.rhs == (schema.attributes.difference(mvd_init.lhs)).difference(mvd_init.rhs)

    def is_augmentation_mvd(mvd, mvd_init, a: set, schema: Schema):
        return type(mvd) == MVDep and type(mvd_init) == MVDep \
            and mvd.lhs == mvd_init.lhs.union(a) \
            and mvd.rhs.difference(mvd_init.rhs) < a and a < schema.attributes

    def is_transitivity_mvd(mvd, mvd_lhs, mvd_rhs):
        return type(mvd) == MVDep and type(mvd_lhs) == MVDep and type(mvd_rhs) == MVDep \
            and mvd.lhs == mvd_lhs.lhs \
            and mvd_lhs.rhs == mvd_rhs.lhs \
            and mvd.rhs == mvd_rhs.rhs.difference(mvd_rhs.lhs)

    def is_replication_mvd(mvd, fd):
        return type(fd) == FDep and type(mvd) == MVDep \
            and fd.lhs == mvd.lhs and fd.rhs == mvd.rhs 

    def is_coalescence_mvd(fd, mvd_init, fd_init):
        return type(fd) == FDep and type(mvd_init) == MVDep and type(fd_init) == FDep \
            and fd.lhs == mvd_init.lhs and fd.rhs == fd_init.rhs \
            and fd_init.rhs < mvd_init.rhs \
            and len(fd_init.lhs.intersection(mvd_init.rhs)) == 0

    def is_union_mvd(mvd, mvd_lhs, mvd_rhs):
        return type(mvd) == MVDep and type(mvd_lhs) == MVDep and type(mvd_rhs) == MVDep \
            and mvd.lhs == mvd_lhs.lhs \
            and mvd.lhs == mvd_rhs.lhs \
            and mvd.rhs == mvd_lhs.rhs.union(mvd_rhs.rhs)

    def is_intersection_mvd(mvd, mvd_lhs, mvd_rhs):
        return type(mvd) == MVDep and type(mvd_lhs) == MVDep and type(mvd_rhs) == MVDep \
            and mvd.lhs == mvd_lhs.lhs \
            and mvd.lhs == mvd_rhs.lhs \
            and mvd.rhs == mvd_lhs.rhs.intersection(mvd_rhs.rhs)

    def is_difference_mvd(mvd, mvd_lhs, mvd_rhs):
        return type(mvd) == MVDep and type(mvd_lhs) == MVDep and type(mvd_rhs) == MVDep \
            and mvd.lhs == mvd_lhs.lhs \
            and mvd.lhs == mvd_rhs.lhs \
            and mvd.rhs == mvd_lhs.rhs.difference(mvd_rhs.rhs)
