from ast import Attribute


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

    def copy(self):
        return FDep(self.lhs.copy(), self.rhs.copy())

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

    def copy(self):
        return MVDep(self.lhs.copy(), self.rhs.copy())

    def to_result(self):
        """
        Returns the FDep as the form of [LHS, RHS]
        as required by the assignment.
        """
        return "{} ->> {}".format(''.join(sorted(self.lhs)), ''.join(sorted(self.rhs)))

class Tuple:
    """
    A class used to represent a tuple.

    Attributes
    ----------
    attributes : []
        The list of attributes in the schema
    values : []
        The values in the tuples given the set of attributes.
    """
    def __init__(self, attributes=[], values=[]):
        self.attributes = attributes 
        self.values = values 

    def __repr__(self):
        return str(self.values)

    def copy(self):
        return Tuple(self.attributes.copy(), self.values.copy())

    def get_val(self, attribute):
        val = []
        for attr in sorted(set(attribute)):
            val.append(self.values[self.attributes.index(attr)])
        return tuple(val)

    def set_val(self, attribute, vals):
        attributes = sorted(set(attribute))
        for i in range(0, len(attributes)):
            attr = attributes[i]
            val = vals[i]
            self.values[self.attributes.index(attr)] = val

    def __eq__(self, other):
        return self.values == other.values


class Schema: 
    """
    A class used to represent a schema.
    ...

    Attributes
    ----------
    attributes : []
        The list of attributes in the schema
    tuples : Tuple[]
        The list of tuples
    deps: []
        The list of dependencies 
    target
        The target dependency
    """

    def __init__(self, attributes='', tuples=[], deps=[], target=None):
        self.attributes = attributes
        self.tuples = tuples
        self.deps = deps
        self.target = target

    def __eq__(self, other):
        if type(other) != Schema:
            return False
        return self.tuples == other.tuples

    def copy(self):
        return Schema(self.attributes.copy(), \
            self.tuples.copy(), \
            self.deps.copy(), \
            self.target)

    def add_dep(self, dep):
        self.deps.append(dep)

    def add_tuple(self, values=[]):
        tuple = Tuple(self.attributes, values)
        self.tuples.append(tuple)

    def init(self):
        if len(self.tuples) == 0:
            self.add_tuple(['1'] * len(self.attributes))
            self.add_tuple(['2'] * len(self.attributes))

    def proc(self, schemas):
        counter = '2'
        for schema in schemas:
            tuple =  Tuple(self.attributes, [counter] * len(self.attributes))
            for attribute in sorted(set(schema)):
                tuple.set_val(attribute, '1')

            self.tuples.append(tuple)
            counter = str(int(counter) + 1)

    def print_schema(self):
        print('\t'.join(self.attributes))
        for tuple in self.tuples:
            print('\t'.join(tuple.values))
        print()

    def modify(self, dep):
        if type(dep) == FDep:
            to_change = dict()

            for tuple in self.tuples:
                val = tuple.get_val(dep.lhs)
                if not val in to_change:
                    to_change[val] = tuple.get_val(dep.rhs)
                else:
                    to_change[val] = min(tuple.get_val(dep.rhs), to_change[val])

            new_tuples = []
            for tuple in self.tuples:
                new_tuple = tuple.copy()
                val = new_tuple.get_val(dep.lhs)
                new_val = to_change[val]
                new_tuple.set_val(dep.rhs, new_val)
                new_tuples.append(new_tuple)
            self.tuples = new_tuples 
        else: 
            to_duplicate = dict()
            for tuple in self.tuples:
                val = tuple.get_val(dep.lhs)
                if not val in to_duplicate:
                    to_duplicate[val] = [tuple]
                else: 
                    to_duplicate[val].append(tuple)  

            for lhs in to_duplicate.keys():
                to_duplicate_tuples = to_duplicate[lhs]
                if len(to_duplicate_tuples) != 2:
                    continue

                tup_1, tup_2 = to_duplicate_tuples
                tup_3 = tup_1.copy()
                tup_4 = tup_2.copy()
                tup_3.set_val(dep.rhs, tup_2.get_val(dep.rhs))
                tup_4.set_val(dep.rhs, tup_1.get_val(dep.rhs))
                self.add_tuple(tup_3.values)
                self.add_tuple(tup_4.values)

    def verify(self):
        if type(self.target) == FDep:
            checker = dict()
            for tuple in self.tuples:
                val = tuple.get_val(self.target.lhs)
                res = tuple.get_val(self.target.rhs)
                if not val in checker:
                    checker[val] = set()
                    
                checker[val].add(res)
            
            for key in checker:
                if len(checker[key]) > 1:
                    return False

            return True 
        else:
            for tuple in self.tuples:
                if min(tuple.values) == max(tuple.values):
                    return True 

            return False


    def chase(self):
        self.print_schema()
        print("{}: {}".format(type(self.target), self.target.lhs))
        for attr in self.target.lhs:
            for tuple in self.tuples: 
                tuple.set_val(attr, '1')

        self.print_schema()

        old_schema = None 
        while (self != old_schema):
            old_schema = self.copy()

            for counter in range(0, len(self.deps)):
                fd_to_handle = self.deps[counter]

                print(fd_to_handle)
                self.modify(fd_to_handle)
                self.print_schema()

        if self.verify():
            print("Target: {} OK".format(self.target))
        else: 
            print("Target: {} FAILED".format(self.target))


