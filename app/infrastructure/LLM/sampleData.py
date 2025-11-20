sample_lecture = """
Python programming language provides two types of loops – For loop and While loop to handle looping requirements. Python provides three ways for executing the loops.

While all the ways provide similar basic functionality, they differ in their syntax and condition-checking time. In this article, we will look at Python loops and understand their working with the help of examples.

While Loop in Python
In Python, a while loop is used to execute a block of statements repeatedly until a given condition is satisfied. When the condition becomes false, the line immediately after the loop in the program is executed.

While Loop Syntax:

poster
while expression:
    statement(s)
All the statements indented by the same number of character spaces after a programming construct are considered to be part of a single block of code. Python uses indentation as its method of grouping statements. 

Let’s learn how to use while loop in Python with Examples:

Example of Python While Loop 


Let’s see a simple example of while loop in Python. The given Python code uses a ‘while' loop to print “Hello Geek” three times by incrementing a variable called ‘count' from 1 to 3.


count = 0
while (count < 3):
    count = count + 1
    print("Hello Geek")
Output
Hello Geek
Hello Geek
Hello Geek
Using else statement with While Loop in Python
The else clause is only executed when your while condition becomes false. If you break out of the loop, or if an exception is raised, it won’t be executed. 

Syntax of While Loop with else statement:

while condition:
     # execute these statements
else:
     # execute these statements
Examples of While Loop with else statement:

Here is an example of while loop with else statement in Python:


The code prints “Hello Geek” three times using a ‘while' loop and then, after the loop, it prints “In Else Block” because there is an “else” block associated with the ‘while' loop.


count = 0
while (count < 3):
    count = count + 1
    print("Hello Geek")
else:
    print("In Else Block")
Output
Hello Geek
Hello Geek
Hello Geek
In Else Block
Infinite While Loop in Python
If we want a block of code to execute infinite number of time, we can use the while loop in Python to do so.

The code uses a ‘while' loop with the condition (count == 0). This loop will only run as long as count is equal to 0. Since count is initially set to 0, the loop will execute indefinitely because the condition is always true.


count = 0
while (count == 0):
    print("Hello Geek")
Note: It is suggested not to use this type of loop as it is a never-ending infinite loop where the condition is always true and you have to forcefully terminate the compiler.

For Loop in Python
For loops are used for sequential traversal. For example: traversing a list or string or array etc. In Python, there is “for in” loop which is similar to foreach loop in other languages. Let us learn how to use for loop in Python for sequential traversals with examples.

For Loop Syntax:

for iterator_var in sequence:
    statements(s)
It can be used to iterate over a range and iterators.

Example:

The code uses a Python for loop that iterates over the values from 0 to 3 (not including 4), as specified by the range(0, n) construct. It will print the values of ‘i' in each iteration of the loop.


n = 4
for i in range(0, n):
    print(i)
Output
0
1
2
3
Example with List, Tuple, String, and Dictionary Iteration Using for Loops in Python
We can use for loop to iterate lists, tuples, strings and dictionaries in Python.

The code showcases different ways to iterate through various data structures in Python. It demonstrates iteration over lists, tuples, strings, dictionaries, and sets, printing their elements or key-value pairs.

The output displays the contents of each data structure as it is iterated.


print("List Iteration")
l = ["geeks", "for", "geeks"]
for i in l:
    print(i)
print("\nTuple Iteration")
t = ("geeks", "for", "geeks")
for i in t:
    print(i)
print("\nString Iteration")
s = "Geeks"
for i in s:
    print(i)
print("\nDictionary Iteration")
d = dict()
d['xyz'] = 123
d['abc'] = 345
for i in d:
    print("%s  %d" % (i, d[i]))
print("\nSet Iteration")
set1 = {1, 2, 3, 4, 5, 6}
for i in set1:
    print(i),
Output
List Iteration
geeks
for
geeks

Tuple Iteration
geeks
for
geeks

String Iteration
G
e
e
k
s

Dictionary Iteration
xyz  123
abc  345

Set Iteration
1
2
3
4
5
6
Iterating by the Index of Sequences
We can also use the index of elements in the sequence to iterate. The key idea is to first calculate the length of the list and in iterate over the sequence within the range of this length. See the below

Example: This code uses a ‘for' loop to iterate over a list and print each element. It iterates through the list based on the index of each element, obtained using ‘range(len(list))'. The result is that it prints each item in the list on separate lines.


list = ["geeks", "for", "geeks"]
for index in range(len(list)):
    print(list[index])
Output
geeks
for
geeks
Using else Statement with for Loop in Python
We can also combine else statement with for loop like in while loop. But as there is no condition in for loop based on which the execution will terminate so the else block will be executed immediately after for block finishes execution. 

In this code, the ‘for' loop iterates over a list and prints each element, just like in the previous example. However, after the loop is finished, the “else” block is executed. So, in this case, it will print “Inside Else Block” once the loop completes.



list = ["geeks", "for", "geeks"]
for index in range(len(list)):
    print(list[index])
else:
    print("Inside Else Block")
Output
geeks
for
geeks
Inside Else Block
Nested Loops
Python programming language allows to use one loop inside another loop which is called nested loop. Following section shows few examples to illustrate the concept. 

Nested Loops Syntax:

for iterator_var in sequence:
   for iterator_var in sequence:
       statements(s)
   statements(s)
The syntax for a nested while loop statement in the Python programming language is as follows: 

while expression:
   while expression: 
       statement(s)
   statement(s)
A final note on loop nesting is that we can put any type of loop inside of any other type of loop. For example, a for loop can be inside a while loop or vice versa.

Example: This Python code uses nested ‘for' loops to create a triangular pattern of numbers. It iterates from 1 to 4 and, in each iteration, prints the current number multiple times based on the iteration number. The result is a pyramid-like pattern of numbers.


from __future__ import print_function
for i in range(1, 5):
    for j in range(i):
        print(i, end=' ')
    print()
Output
1 
2 2 
3 3 3 
4 4 4 4 
Loop Control Statements
Loop control statements change execution from their normal sequence. When execution leaves a scope, all automatic objects that were created in that scope are destroyed. Python supports the following control statements. 

Continue Statement
The continue statement in Python returns the control to the beginning of the loop.

Example: This Python code iterates through the characters of the string ‘geeksforgeeks’. When it encounters the characters ‘e’ or ‘s’, it uses the continue statement to skip the current iteration and continue with the next character. For all other characters, it prints “Current Letter :” followed by the character. So, the output will display all characters except ‘e’ and ‘s’, each on a separate line.


for letter in 'geeksforgeeks':
    if letter == 'e' or letter == 's':
        continue
    print('Current Letter :', letter)
Output
Current Letter : g
Current Letter : k
Current Letter : f
Current Letter : o
Current Letter : r
Current Letter : g
Current Letter : k
Break Statement
The break statement in Python brings control out of the loop.

Example: In this Python code, it iterates through the characters of the string ‘geeksforgeeks’. When it encounters the characters ‘e’ or ‘s’, it uses the break statement to exit the loop. After the loop is terminated, it prints “Current Letter :” followed by the last character encountered in the loop (either ‘e’ or ‘s’). So, the output will display “Current Letter :” followed by the first occurrence of ‘e’ or ‘s’ in the string.


for letter in 'geeksforgeeks':
    if letter == 'e' or letter == 's':
        break
 
print('Current Letter :', letter)
Output
Current Letter : e
Pass Statement
We use pass statement in Python to write empty loops. Pass is also used for empty control statements, functions and classes.

Example: This Python code iterates through the characters of the string ‘geeksforgeeks’ using a ‘for' loop. However, it doesn’t perform any specific action within the loop, and the ‘pass' statement is used. After the loop, it prints “Last Letter :” followed by the last character in the string, which is ‘s’.


for letter in 'geeksforgeeks':
    pass
print('Last Letter :', letter)
Output
Last Letter : s
How for loop in Python works internally?
Before proceeding to this section, you should have a prior understanding of Python Iterators.

Firstly, lets see how a simple for loop looks like.

Example: This Python code iterates through a list called fruits, containing “apple”, “orange” and “kiwi.” It prints each fruit name on a separate line, displaying them in the order they appear in the list.


fruits = ["apple", "orange", "kiwi"]
 
for fruit in fruits:
 
    print(fruit)
Output
apple
orange
kiwi
Here we can see the for loops iterates over iterable object fruit which is a list. Lists, sets, dictionaries are few iterable objects while an integer object is not an iterable object. For loops can iterate over any of these iterable objects.

This Python code manually iterates through a list of fruits using an iterator. It prints each fruit’s name one by one and stops when there are no more items in the list.


fruits = ["apple", "orange", "kiwi"]
iter_obj = iter(fruits)
while True:
    try:
        fruit = next(iter_obj)
        print(fruit)
    except StopIteration:
        break
Output
apple
orange
kiwi
We can see that under the hood we are calling iter() and next() method. 

We have covered Python Loops in this article. We also saw how to use for loop, while loop and nested loop in Python. This article provides different use-case scenarios and examples to demonstrate working of loops and give clear understanding.
"""

sample_concepts = [
"For loop",
"While loop",
"Loop control statements",
"Syntax",
"Iteration",
"Indentation",
"Else statement",
"Infinite loop",
"Nested loops",
"Continue statement",
"Break statement",
"Pass statement",
"Iterator",
# "Iterable object"
]

sample_prereqID_response = {
        "For loop": ["Syntax", "Iteration", "Indentation"],
        "While loop": ["Syntax", "Iteration", "Indentation"],
        "Loop control statements": ["For loop", "While loop"],
        "Syntax": [],
        "Iteration": [],
        "Indentation": [],
        "Else statement": ["For loop", "While loop"],
        "Infinite loop": ["While loop"],
        "Nested loops": ["For loop", "While loop"],
        "Continue statement": ["For loop", "While loop"],
        "Break statement": ["For loop", "While loop"],
        "Pass statement": ["For loop", "While loop"],
        "Iterator": ["Iterable object"],
    }
