# Dependency Solver 

Solves common questions with regards to functional dependencies (NOT multi-valued dependencies)

## Usage 

`python main.py <schema_file> <commands_file> <output_file>`

1. `schema_file` contains the attributes in the schema in the first line, 
followed by a sequence of functional dependencies 

2. `commands_file` contains the commands to get the necessary results for. 

3. `output_file` the file to direct output to. 

## Notes 

There will be temp files outputted, which represent the steps required to calculate 
a certain minimal cover.

## Commands available

1. get_attribute_closures
2. get_essential_attr_closures
3. get_prime_attributes
4. get_superkeys
5. get_candidate_keys
6. get_fd_closure
7. get_minimal_cover_from_fds
8. get_all_minimal_covers_from_fds
9. get_minimal_cover
10. get_all_minimal_covers
11. is_in_bcnf
12. is_in_3nf
13. is_in_2nf
14. decomposition_algorithm
15. is_bcnf_decomposition_dependency_preserving
16. synthesis_algorithm
17. is_3nf_synthesis_in_bcnf
