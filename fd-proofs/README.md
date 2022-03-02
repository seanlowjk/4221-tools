# Rules Prover 

A simple tool to help with proving the correctness of 
Functional and Multi-Valued Dependencies.

## Usage 

`python main.py <input_file>`

## Syntax 

The first line should be a list of all the attributes 
The following lines are the derived FDs followed by their rules. 
For example: 

```
ABCDE
E->>AD Given
B->D Given 
E->D Coalescence 1,2
```

## FD Rules Syntax 

```
ABCDE
A->B Given 
AC->BC Augmentation 1 C
AC->A Reflexivity
AC->B Transitivity 3,1
```

## MVD Rules Syntax 

```
ABCDE
A->>BE Given 
C->>D Given
E->A Given
A->>CD Complementation 1
BCD->>BD Augmentation 2 BD
E->>A Replication 3
E->>BE Transitivity 6,1
```

```
ABCDE
E->>AD Given
B->D Given 
E->D Coalescence 1,2
```

```
ABCDE
A->>BC Given 
A->>CD Given 
A->>BCD Union 1,2
A->>C Intersection 1,2 
A->>B Difference 1,2 
```