from itertools import combinations
from random import random
from math import ceil

import sys

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
        return [sorted(self.lhs), sorted(self.rhs)]

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


class FDSet:
    """
    A class used to represent R and Sigma, representing the attributes
    and the functional dependencies in a database instance.
    """

    def __init__(self, attributes: list = [], fds: list = []):
        self.attributes = set(attributes)
        self.fds = []
        self.bcnf_decomposition = []
        self._3nf_decomposition = []

        for fd in fds:
            self.add_fd(fd)

    def __str__(self):
        return f"R{sorted(self.attributes)}\nF{sorted(self.fds)}"

    def __eq__(self, other):
        """
        Checks if the FDSet is equal to another FDSet or not.
        """
        if not isinstance(other, FDSet):
            return False

        for fd in other.fds:
            clos = self.get_attribute_closure(fd.lhs)
            if not (fd.rhs).issubset(clos.closure()):
                return False

        return True

    def issubset(self, other):
        """
        Checks if the FDs of this FDSet is a subset of
        a set of FDs from another FDSet or not.
        """
        if not isinstance(other, FDSet):
            return False

        this_fds, other_fds = set(self.fds), set(other.fds)
        return this_fds.issubset(other_fds)

    def add_attributes(self, attributes: list):
        """
        Appends attributes to the database instance.
        """
        self.attributes = self.attributes.union(set(attributes))

    def add_fd(self, fd: FDep) -> None:
        """
        Appends attributes to the database instance.
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

    def get_candidate_keys(self) -> list:
        """
        Gets all the candidate keys of the database instance.
        """
        superkeys = self.get_superkeys()
        keys = []

        for superkey in superkeys:
            is_candidate_key = True

            for superkey_2 in superkeys:
                if superkey != superkey_2 and set(superkey_2).issubset(set(superkey)):
                    is_candidate_key = False
                    break

            if is_candidate_key:
                keys.append(superkey)

        return sorted(keys)

    def is_prime_attribute(self, attr: str) -> bool:
        """
        Returns true if the attribute is a prime attribute.
        """
        assert len(attr) == 1

        keys = self.get_candidate_keys()

        for key in keys:
            if attr in key:
                return True

        return False

    def get_prime_attributes(self) -> list:
        """
        Returns all the prime attributes of the
        database instance.
        """
        prime_attributes = []
        for attr in self.attributes:
            if self.is_prime_attribute(attr):
                prime_attributes.append(attr)

        # Sort the prime attributes for readaibility purposes.
        return sorted(prime_attributes)

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

    def get_minimal_cover_from_fds(self):
        """
        Returns the minimal cover reachable from the set of
        fds of the minimal cover.
        """
        return self.get_minimal_cover(self.fds)

    def get_minimal_cover(self, fd_set=None):
        """
        Returns the minimal cover reachable from the set of
        fds provided as an argument.
        """
        if fd_set is None:
            # If no set of FDs are provided, take
            # Sigma+, the FDep closure of the database instance.
            fd_set = self.get_fd_closure()

        closures = self.get_attribute_closures()

        # Step 1: Simplify the LHS of all FDs
        fd_set_1 = MinimalCoverUtils.simplify_lhs(fd_set, closures)

        # Step 2: Remove FDs that can do not contribute to the attribute closure.
        fd_set_2 = MinimalCoverUtils.remote_redundant_fds(fd_set_1, self.attributes)

        ### BEGIN WRITE ###
        with open('temp-{}.txt'.format(ceil(random() * 10000)), 'w') as out:
            out.write(sys._getframe(1).f_code.co_name + "\n")
            for fd in fd_set:
                out.write(str(fd) + '\n')
            out.write('\n')

            out.write("Remove Redundant LHS\n")
            for fd in set(fd_set).difference(set(fd_set_1)):
                out.write(str(fd) + '\n')
            out.write('\n')

            out.write("Remove Redundant FDs\n")
            for fd in set(fd_set_1).difference(set(fd_set_2)):
                out.write(str(fd) + '\n')
            out.write('\n')

            out.write("Minimal Cover\n")
            for fd in sorted(fd_set_2):
                out.write(str(fd) + '\n')
            out.write('\n')

        ### END WRITE ###

        # Sort the FDs for readaibility purposes.
        return sorted(fd_set_2)

    def get_all_minimal_covers_from_fds(self):
        """
        Returns all the minimal covers reachable from the set of
        fds of the minimal cover.
        """
        return self.get_all_minimal_covers(self.fds)

    def get_compact_fds(self, fd_set = None):
        """
        Returns the set of fds in compact form.
        """
        if fd_set is None:
            # If no set of FDs are provided, take the fds
            fd_set = self.fds

        fd_dict = {}
        for fd in fd_set:
            lhs = ''.join(fd.lhs)
            rhs = ''.join(fd.rhs)
            if lhs in fd_dict.keys():
                fd_dict[lhs] += rhs 
            else:
                fd_dict[lhs] = rhs 

        compact_fds = []
        for fd_lhs in fd_dict:
            fd_rhs = fd_dict[fd_lhs]
            compact_fd = FDep(set(list(fd_lhs)), set(list(fd_rhs)))
            compact_fds.append(compact_fd)

        return compact_fds
    

    def get_all_minimal_covers(self, fd_set=None):
        """
        Returns all the minimal covers reachable from the set of
        fds provided as an argument.
        """
        # Retrieve the fds from a sample minimal cover.
        example_minimal_cover_fds = self.get_minimal_cover(fd_set)

        if fd_set is None:
            # If no set of FDs are provided, take
            # Sigma+, the FDep closure of the database instance.
            fd_set = self.get_fd_closure()

        attribute_closures = self.get_attribute_closures()

        # Step 1: Simplify the LHS of all FDs
        fd_set_1 = MinimalCoverUtils.simplify_lhs(fd_set, attribute_closures)

        # Step 2: Permutate through all possible combinations of fds to
        #         find possible minimal covers.
        minimal_covers = []

        for num_fds in range(1, len(fd_set_1) + 1):
            for possible_minimal_cover_fds in combinations(fd_set_1, num_fds):
                possible_minimal_cover_fds = list(possible_minimal_cover_fds)

                # Calculate the sample minimal cover and possible minimal covers.
                example_minimal_cover = FDSet(
                    fds=example_minimal_cover_fds, attributes=self.attributes
                )
                possible_cover = FDSet(
                    fds=possible_minimal_cover_fds, attributes=self.attributes
                )

                # If the set of FDs from both minimal covers are equivalent.
                if possible_cover == example_minimal_cover:
                    can_add_possible_cover = True

                    for cover in minimal_covers:
                        # If there already exists a minimal cover which has a subset
                        # of FDs of the possible minimal cover, DO NOT add the
                        # possible minimal cover.
                        if cover.issubset(possible_cover):
                            can_add_possible_cover = False
                            break
                    if can_add_possible_cover:
                        minimal_covers.append(possible_cover)

        return [cover.fds for cover in minimal_covers]

    def is_in_bcnf(self):
        """
        Returns true if the database instance is in BCNF
        """
        if len(self.attributes) < 2:
            return True

        superkeys = self.get_superkeys()
        for fd in self.fds:
            if not fd.is_trivial() and not sorted(fd.lhs) in superkeys: 
                return False 

        return True 

    def is_in_3nf(self):
        """
        Returns true if the database instance is in 3NF
        """
        if self.is_in_bcnf():
            return True

        superkeys = self.get_superkeys()
        prime_attributes = self.get_prime_attributes()
        for fd in self.fds:
            if not fd.is_trivial() and not sorted(fd.lhs) in superkeys: 
                for attribute in sorted(fd.rhs):
                    if attribute not in prime_attributes:
                        return False

        return True 

    def is_in_2nf(self):
        """
        Returns true if the database instance is in 2NF
        """
        if self.is_in_3nf():
            return True

        superkeys = self.get_superkeys()
        prime_attributes = self.get_prime_attributes()
        for fd in self.fds:
            if not fd.is_trivial(): 
                has_all_prime_attributes = True
                for attribute in sorted(fd.rhs):
                    if attribute not in prime_attributes:
                        return False

                if not has_all_prime_attributes:
                    for superkey in superkeys: 
                        if sorted(fd.lhs) < superkey:
                            return False 

        return True 

    def init_child_FD_set(self, new_attrs):
        """
        Initialized a child FD Set given a set of 
        new_attrs and some fds which can be implied
        in the child FD Set.
        """
        new_fds = []

        for fd in self.get_fd_closure():
            if fd.lhs <= new_attrs and fd.rhs <= new_attrs:
                new_fds.append(fd)

        return FDSet(sorted(new_attrs), new_fds)

    def decomposition_algorithm(self):
        """
        Returns a list of FDSets which are in BCNF
        based on the decomposition algorithm learnt in 
        the lecture.
        """
        if len(self.bcnf_decomposition) > 0:
            return self.bcnf_decomposition

        if self.is_in_bcnf():
            return [self]

        superkeys = self.get_superkeys()

        violating_fd = None 
        for fd in self.fds:
            if not fd.is_trivial() and not sorted(fd.lhs) in superkeys: 
                violating_fd = fd
                break 

        R1 = self.get_attribute_closure(violating_fd.lhs).closure()
        R2 = (self.attributes.difference(R1)).union(violating_fd.lhs)

        FD1 = self.init_child_FD_set(R1)
        FD2 = self.init_child_FD_set(R2)

        self.bcnf_decomposition = FD1.decomposition_algorithm() + FD2.decomposition_algorithm()
        return self.bcnf_decomposition

    def is_bcnf_decomposition_dependency_preserving(self):
        if self.is_in_bcnf():
            return True

        if len(self.bcnf_decomposition) == 0:
            return False 

        derived_fds = []
        for fd_set in self.bcnf_decomposition:
            derived_fds += fd_set.fds

        derived_fd_set = FDSet(sorted(self.attributes), derived_fds)

        derived_fd_closure = derived_fd_set.get_fd_closure()
        original_fd_closure = self.get_fd_closure()
        for fd_clos in derived_fd_closure:
            if not fd_clos in original_fd_closure:
                return False 

        for fd_clos in original_fd_closure:
            if not fd_clos in derived_fd_closure:
                return False 

        return True  

    def synthesis_algorithm(self):
        """
        Returns a list of FDSets which are in 3NF based 
        on the synthesis algorithm learnt in the lecture.
        """
        if len(self._3nf_decomposition) > 0:
            return self._3nf_decomposition

        if self.is_in_3nf():
            return [self]
        
        minimal_cover = self.get_minimal_cover_from_fds()
        compact_minimal_cover = self.get_compact_fds(minimal_cover)

        relation_set = [(fd.lhs).union(fd.rhs) for fd in compact_minimal_cover]
        candidate_keys = [set(key) for key in self.get_candidate_keys()]
        
        has_candidate_key = False 
        for key in candidate_keys:
            for relation in relation_set:
                if key <= relation:
                    has_candidate_key = True 
                    break 

        if not has_candidate_key:
            relation_set.append(candidate_keys[0])

        FD_set_list = []
        for relation in relation_set:
            FD_set = self.init_child_FD_set(relation)
            FD_set_list.append(FD_set)

        synthesis_result = []
        for fd_set in FD_set_list:
            can_add_fd_set = True 
            for fd_set_2 in FD_set_list:
                if fd_set.attributes < fd_set_2.attributes:
                    can_add_fd_set = False 
                    break 

            if can_add_fd_set:
                synthesis_result.append(fd_set)


        self._3nf_decomposition = synthesis_result
        return self._3nf_decomposition

    def is_3nf_synthesis_in_bcnf(self):
        """
        Checks if the 3nf decomposition fd sets
        are in BCNF or not. 
        """
        if self.is_in_3nf():
            return True

        if len(self._3nf_decomposition) == 0:
            return False 

        for fd_set in self._3nf_decomposition:
            if not fd_set.is_in_bcnf():
                return False 

        return True  


class MinimalCoverUtils:
    """
    A class used to abstract the stpes of obtaining
    a minimal cover or a list of possible reachable
    minimal covers.
    """

    def simplify_lhs(fd_set, attribute_closures):
        """
        Returns a new list of fd closures where
        the LHS is simplified.
        """
        fd_set_1 = []
        for fd in fd_set:
            has_added = False
            for closure in attribute_closures:

                if (closure.attributes()).issubset(fd.lhs) and (
                    (fd.rhs).issubset(closure.closure()) or fd.rhs == closure.closure()
                ):
                    # If the LHS of the FDep can be simplified, we simplify it.
                    has_added = True
                    new_fd = FDep(closure.attributes(), fd.rhs)
                    if not new_fd in fd_set_1:
                        fd_set_1.append(new_fd)
                    break

            if not has_added and not fd in fd_set_1:
                fd_set_1.append(fd)

        return fd_set_1

    def remote_redundant_fds(fd_set, attributes: set):
        """
        Returns a new list of fd closures which are not
        redundant or trivial.
        """
        fd_set_1 = []
        while fd_set_1 != fd_set:  # While an FDep has been deleted.
            fd_set_1 = fd_set.copy()

            for fd in fd_set:
                fd_set_temp = fd_set.copy()
                fd_set_temp.remove(fd)

                # Calculate the closures attribute closure of the attributes of the
                # LHS of the FDep with and without the remove FDep.
                original_attribute_closure = FDSet(
                    fds=fd_set, attributes=attributes
                ).get_attribute_closure(fd.lhs)
                new_attribute_closure = FDSet(
                    fds=fd_set_temp, attributes=attributes
                ).get_attribute_closure(fd.lhs)

                # If the attribute closures are requivalent, this suggests
                # that the FDep is reundant. Hence, we can remove it.
                if original_attribute_closure == new_attribute_closure:
                    fd_set = fd_set_temp.copy()
                    break

        # Return the set of FDs if there is no more reundant FDep
        # that is being removed.
        return fd_set_1
