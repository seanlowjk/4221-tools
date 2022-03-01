# Rules Prover 

A simple tool to help with proving the correctness of 
Functional and Multi-Valued Dependencies via the Chase.

## Usage 

`python main.py <input_file>`

## Syntax 

Sample: 

```
ABCDEG
AB->C
AB->>E
CD->>AB
RESULT
CD->>E
```

```
ABCDE
A->BC
B->A
C->D
DISTINGUISHED
AE CD ABC
```

- The first line contains the attributes to be used 
- The second to third last line contains the FDs / MVDs in the schema 
- The second last line contains the type:
  1. `RESULT` checks if you want to prove the correctness of the FD / MVD 
  2. `DISTINGUISHED` checks if you want to prove the lossless join property of some fragments 
- The last line contains the target.  
