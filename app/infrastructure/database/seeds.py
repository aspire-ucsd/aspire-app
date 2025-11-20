import logging
import random
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable

from sqlmodel import SQLModel, Session
from app.domain.models.trigger_event import TriggerEventCreate, TriggerEvent

logger = logging.getLogger(__name__)

# TODO implement your own data seeding or remove this code. Also update app/api/app.py:register_events function

def _populate_table(
    db: Session, table: SQLModel, values: Iterable[Dict[str, Any]],
):
    name = table.__tablename__
    logger.info(f"Seeding table {name}")
    for v in values:
        db.add(table.from_orm(v))
    db.commit()
    logger.info(f"Seeded table {name} successfully")

# def _populate_trigger_events_test(db: Session):
#     concepts = ['Operating System Fundamentals', 'Understanding File Systems', 'Path Specification', 'Directory Navigation', 'File Paths, Absolute and Relative Paths', 'File Formats', 'File Operations', 'File Modes', 'Text File Handling', 'Data Parsing Techniques', 'Python Libraries', 'Basic Python Syntax', 'Sequential Execution', 'Variables', 'Types of Data', 'Integers', 'Floats', 'Strings', 'Boolean Expressions', 'Expressions', 'Conditionals', 'If Statement', 'Else Statement', 'Elif Statement', 'Complex Conditionals', 'Nested Conditionals', 'Control Flow', 'Loops', 'For Loops', 'While Loops', 'Continue Statement', 'Break Statement', 'Nested Loops', 'Modulo Operator', 'Introduction to Range', 'List Comprehensions', 'Membership Checking', 'Iterables', 'Lists', 'Dictionaries', 'Tuples', 'Slicing Lists', 'Looping Through Lists', 'Enumerate Function', 'Sorting Lists', 'Reverse Parameter', 'Nested Lists', 'Key/Value Pairs', 'Updating Dictionaries', 'Adding Entries', 'Deleting Dictionaries', 'Merging Dictionaries', 'Iterating Through Dictionaries', 'Nested Dictionaries', 'Function Definition', 'Advantages of Functions', 'Executing a Function', 'Default Values', 'Positional Arguments', 'Returning Multiple Values', 'Namespace', 'Lambda Functions', 'Arbitrary Arguments (*args)', 'Keyword Arbitrary Arguments (**kwargs)', 'Classes Definition', 'Objects', 'Methods', 'Instantiating a Class', 'Instance Attributes', 'init method', 'self keyword', 'Code Style', 'Indentation', 'Multi-Line Strings', 'Len Operator', 'Indexing Strings', 'Slicing Strings', 'Looping Through Strings', 'Modifying Case', 'Replacing Characters', 'Concatenating Strings', 'Splitting Strings', 'String Manipulation', 'Indexed Access', 'Escape Sequences', 'In-Place Operations', 'Definition of Arguments', 'Method Usage', 'Global and Local Variables', 'LIFO Principles', 'Memory Concepts', 'Matrix Concepts', 'NumPy Definition', 'NumPy.ndarray', 'np.arange()', 'Converting from a List to Array', 'Vector Operations', 'Arithmetic Operations', 'Descriptive Statistics', 'Mean in NumPy', 'Median in NumPy', 'Matrices in NumPy']

#     start_date, end_date = datetime(year=2020, month=1, day=1), datetime(year=2024, month=1, day=1)
#     date_choices = [start_date]

#     while start_date < end_date:
#         # print(start_date)
#         start_date += timedelta(days=2.0)
#         date_choices.append(start_date)

#     values = []
#     for concept in concepts:
#         for _ in range(random.randint(0, 5)):
#             date = random.choice(date_choices)
#             score = random.random()
#             weight = random.random()
#             test_event = TriggerEventCreate(datetime_stamp=date, student_id=107, concept=concept, value=score, weight=weight)
#             values.append(test_event)

#     _populate_table(db, TriggerEvent, values)




def _populate_trigger_events_test(db: Session):
    concepts = [ (
    107,
    'Operating System Fundamentals',
    1.0,
    2.0,
    1.0,
    1
    ),
    (
    107,
    'Understanding File Systems',
    1.0,
    2.0,
    1.0,
    1
    ),
    (107, 'Path Specification', 1.0, 2.0, 0.98, 1),
    (107, 'Directory Navigation', 1.0, 2.0, 0.97, 1),
    (
    107,
    'File Paths, Absolute and Relative Paths',
    1.0,
    2.0,
    0.96,
    1
    ),
    (107, 'File Formats', 1.0, 2.0, 0.95, 1),
    (107, 'File Operations', 1.0, 2.0, 0.94, 1),
    (107, 'File Modes', 1.0, 2.0, 0.93, 1),
    (107, 'Text File Handling', 1.0, 2.0, 0.92, 1),
    (107, 'Data Parsing Techniques', 1.0, 2.0, 0.91, 1),
    (107, 'Python Libraries', 1.0, 2.0, 0.9, 1),
    (107, 'Basic Python Syntax', 1.0, 2.0, 0.89, 1),
    (107, 'Sequential Execution', 1.0, 2.0, 0.88, 1),
    (107, 'Variables', 1.0, 2.0, 0.87, 1),
    (107, 'Types of Data', 1.0, 2.0, 0.86, 1),
    (107, 'Integers', 1.0, 2.0, 0.85, 1),
    (107, 'Floats', 1.0, 2.0, 0.85, 1),
    (107, 'Strings', 1.0, 2.0, 0.84, 1),
    (107, 'Boolean Expressions', 1.0, 2.0, 0.83, 1),
    (107, 'Expressions', 1.0, 2.0, 0.82, 1),
    (107, 'Conditionals', 1.0, 2.0, 0.81, 1),
    (107, 'If Statement', 1.0, 2.0, 0.8, 1),
    (107, 'Else Statement', 1.0, 2.0, 0.79, 1),
    (107, 'Elif Statement', 1.0, 2.0, 0.78, 1),
    (107, 'Complex Conditionals', 1.0, 2.0, 0.77, 1),
    (107, 'Nested Conditionals', 1.0, 2.0, 0.76, 1),
    (107, 'Control Flow', 1.0, 2.0, 0.75, 1),
    (107, 'Loops', 1.0, 2.0, 0.74, 1),
    (107, 'For Loops', 1.0, 2.0, 0.73, 1),
    (107, 'While Loops', 1.0, 2.0, 0.72, 1),
    (107, 'Continue Statement', 1.0, 2.0, 0.71, 1),
    (107, 'Break Statement', 1.0, 2.0, 0.7, 1),
    (107, 'Nested Loops', 1.0, 2.0, 0.69, 1),
    (107, 'Modulo Operator', 1.0, 2.0, 0.68, 1),
    (107, 'Introduction to Range', 1.0, 2.0, 0.67, 1),
    (107, 'List Comprehensions', 1.0, 2.0, 0.66, 1),
    (107, 'Membership Checking', 1.0, 2.0, 0.65, 1),
    (107, 'Iterables', 1.0, 2.0, 0.64, 1),
    (107, 'Lists', 1.0, 2.0, 0.63, 1),
    (107, 'Dictionaries', 1.0, 2.0, 0.62, 1),
    (107, 'Tuples', 1.0, 2.0, 0.61, 1),
    (107, 'Slicing Lists', 1.0, 2.0, 0.6, 1),
    (107, 'Looping Through Lists', 1.0, 2.0, 0.59, 1),
    (107, 'Enumerate Function', 1.0, 2.0, 0.58, 1),
    (107, 'Sorting Lists', 1.0, 2.0, 0.57, 1),
    (107, 'Reverse Parameter', 1.0, 2.0, 0.56, 1),
    (107, 'Nested Lists', 1.0, 2.0, 0.55, 1),
    (107, 'Key/Value Pairs', 1.0, 2.0, 0.54, 1),
    (107, 'Updating Dictionaries', 1.0, 2.0, 0.53, 1),
    (107, 'Adding Entries', 1.0, 2.0, 0.52, 1),
    (107, 'Deleting Dictionaries', 1.0, 2.0, 0.51, 1),
    (107, 'Merging Dictionaries', 1.0, 2.0, 0.5, 1),
    (
    107,
    'Iterating Through Dictionaries',
    1.0,
    2.0,
    0.49,
    1
    ),
    (107, 'Nested Dictionaries', 1.0, 2.0, 0.48, 1),
    (107, 'Function Definition', 1.0, 2.0, 0.47, 1),
    (107, 'Advantages of Functions', 1.0, 2.0, 0.46, 1),
    (107, 'Executing a Function', 1.0, 2.0, 0.45, 1),
    (107, 'Default Values', 1.0, 2.0, 0.44, 1),
    (107, 'Positional Arguments', 1.0, 2.0, 0.43, 1),
    (
    107,
    'Returning Multiple Values',
    1.0,
    2.0,
    0.42,
    1
    ),
    (107, 'Namespace', 1.0, 2.0, 0.41, 1),
    (107, 'Lambda Functions', 1.0, 2.0, 0.4, 1),
    (
    107,
    'Arbitrary Arguments (*args)',
    1.0,
    2.0,
    0.39,
    1
    ),
    (
    107,
    'Keyword Arbitrary Arguments (**kwargs)',
    1.0,
    2.0,
    0.38,
    1
    ),
    (107, 'Classes Definition', 1.0, 2.0, 0.37, 1),
    (107, 'Objects', 1.0, 2.0, 0.36, 1),
    (107, 'Methods', 1.0, 2.0, 0.35, 1),
    (107, 'Instantiating a Class', 1.0, 2.0, 0.34, 1),
    (107, 'Instance Attributes', 1.0, 2.0, 0.33, 1),
    (107, 'init method', 1.0, 2.0, 0.32, 1),
    (107, 'self keyword', 1.0, 2.0, 0.31, 1),
    (107, 'Code Style', 1.0, 2.0, 0.3, 1),
    (107, 'Indentation', 1.0, 2.0, 0.29, 1),
    (107, 'Multi-Line Strings', 1.0, 2.0, 0.28, 1),
    (107, 'Len Operator', 1.0, 2.0, 0.27, 1),
    (107, 'Indexing Strings', 1.0, 2.0, 0.26, 1),
    (107, 'Slicing Strings', 1.0, 2.0, 0.25, 1),
    (107, 'Looping Through Strings', 1.0, 2.0, 0.24, 1),
    (107, 'Modifying Case', 1.0, 2.0, 0.23, 1),
    (107, 'Replacing Characters', 1.0, 2.0, 0.22, 1),
    (107, 'Concatenating Strings', 1.0, 2.0, 0.21, 1),
    (107, 'Splitting Strings', 1.0, 2.0, 0.2, 1),
    (107, 'String Manipulation', 1.0, 2.0, 0.19, 1),
    (107, 'Indexed Access', 1.0, 2.0, 0.18, 1),
    (107, 'Escape Sequences', 1.0, 2.0, 0.17, 1),
    (107, 'In-Place Operations', 1.0, 2.0, 0.16, 1),
    (107, 'Definition of Arguments', 1.0, 2.0, 0.15, 1),
    (107, 'Method Usage', 1.0, 2.0, 0.14, 1),
    (
    107,
    'Global and Local Variables',
    1.0,
    2.0,
    0.13,
    1
    ),
    (107, 'LIFO Principles', 1.0, 2.0, 0.12, 1),
    (107, 'Memory Concepts', 1.0, 2.0, 0.11, 1),
    (107, 'Matrix Concepts', 1.0, 2.0, 0.1, 1),
    (107, 'NumPy Definition', 1.0, 2.0, 0.09, 1),
    (107, 'NumPy.ndarray', 1.0, 2.0, 0.08, 1),
    (107, 'np.arange()', 1.0, 2.0, 0.07, 1),
    (107,'Converting from a List to Array',1.0,2.0,0.06,1
    ),
    (107, 'Vector Operations', 1.0, 2.0, 0.05, 1),
    (107, 'Arithmetic Operations', 1.0, 2.0, 0.04, 1),
    (107, 'Descriptive Statistics', 1.0, 2.0, 0.03, 1),
    (107, 'Mean in NumPy', 1.0, 2.0, 0.02, 1),
    (107, 'Median in NumPy', 1.0, 2.0, 0.01, 1),
    (107, 'Matrices in NumPy', 1.0, 2.0, 0.0, 1)]

    start_date, end_date = datetime(year=2024, month=9, day=1), datetime(year=2024, month=9, day=30)
    date_choices = [start_date]

    while start_date < end_date:
        # print(start_date)
        start_date += timedelta(days=2.0)
        date_choices.append(start_date)

    values = []
    multipliers = [1.1, 0.9, 1.3, 0.7]
    for concept in concepts:
        for _ in range(random.randint(1, 3)):
            date = random.choice(date_choices)
            score = concept[4]
            multiplier = random.choice(multipliers)
            if score * multiplier <= 1:
                score = score * multiplier

            weight = random.random()
            test_event = TriggerEventCreate(datetime_stamp=date, student_id=107, concept=concept[1], value=score, weight=weight)
            values.append(test_event)

    _populate_table(db, TriggerEvent, values)


# def _populate_trigger_events_test(db: Session):
#     concepts = [ (
#     107,
#     'Operating System Fundamentals',
#     1.0,
#     2.0,
#     1.0,
#     1
#     ),
#     (
#     107,
#     'Understanding File Systems',
#     1.0,
#     2.0,
#     1.0,
#     1
#     ),
#     (107, 'Path Specification', 1.0, 2.0, 0.98, 1),
#     (107, 'Directory Navigation', 1.0, 2.0, 0.97, 1),
#     (
#     107,
#     'File Paths, Absolute and Relative Paths',
#     1.0,
#     2.0,
#     0.96,
#     1
#     ),
#     (107, 'File Formats', 1.0, 2.0, 0.95, 1),
#     (107, 'File Operations', 1.0, 2.0, 0.94, 1),
#     (107, 'File Modes', 1.0, 2.0, 0.93, 1),
#     (107, 'Text File Handling', 1.0, 2.0, 0.92, 1),
#     (107, 'Data Parsing Techniques', 1.0, 2.0, 0.91, 1),
#     (107, 'Python Libraries', 1.0, 2.0, 0.9, 1),
#     (107, 'Basic Python Syntax', 1.0, 2.0, 0.89, 1),
#     (107, 'Sequential Execution', 1.0, 2.0, 0.88, 1),
#     (107, 'Variables', 1.0, 2.0, 0.87, 1),
#     (107, 'Types of Data', 1.0, 2.0, 0.86, 1),
#     (107, 'Integers', 1.0, 2.0, 0.85, 1),
#     (107, 'Floats', 1.0, 2.0, 0.85, 1),
#     (107, 'Strings', 1.0, 2.0, 0.84, 1),
#     (107, 'Boolean Expressions', 1.0, 2.0, 0.83, 1),
#     (107, 'Expressions', 1.0, 2.0, 0.82, 1),
#     (107, 'Conditionals', 1.0, 2.0, 0.81, 1),
#     (107, 'If Statement', 1.0, 2.0, 0.8, 1),
#     (107, 'Else Statement', 1.0, 2.0, 0.79, 1),
#     (107, 'Elif Statement', 1.0, 2.0, 0.78, 1),
#     (107, 'Complex Conditionals', 1.0, 2.0, 0.77, 1),
#     (107, 'Nested Conditionals', 1.0, 2.0, 0.76, 1),
#     (107, 'Control Flow', 1.0, 2.0, 0.75, 1),
#     (107, 'Loops', 1.0, 2.0, 0.74, 1),
#     (107, 'For Loops', 1.0, 2.0, 0.73, 1),
#     (107, 'While Loops', 1.0, 2.0, 0.72, 1),
#     (107, 'Continue Statement', 1.0, 2.0, 0.71, 1),
#     (107, 'Break Statement', 1.0, 2.0, 0.7, 1),
#     (107, 'Nested Loops', 1.0, 2.0, 0.69, 1),
#     (107, 'Modulo Operator', 1.0, 2.0, 0.68, 1),
#     (107, 'Introduction to Range', 1.0, 2.0, 0.67, 1),
#     (107, 'List Comprehensions', 1.0, 2.0, 0.66, 1),
#     (107, 'Membership Checking', 1.0, 2.0, 0.65, 1),
#     (107, 'Iterables', 1.0, 2.0, 0.64, 1),
#     (107, 'Lists', 1.0, 2.0, 0.63, 1),
#     (107, 'Dictionaries', 1.0, 2.0, 0.62, 1),
#     (107, 'Tuples', 1.0, 2.0, 0.61, 1),
#     (107, 'Slicing Lists', 1.0, 2.0, 0.6, 1),
#     (107, 'Looping Through Lists', 1.0, 2.0, 0.59, 1),
#     (107, 'Enumerate Function', 1.0, 2.0, 0.58, 1),
#     (107, 'Sorting Lists', 1.0, 2.0, 0.57, 1),
#     (107, 'Reverse Parameter', 1.0, 2.0, 0.56, 1),
#     (107, 'Nested Lists', 1.0, 2.0, 0.55, 1),
#     (107, 'Key/Value Pairs', 1.0, 2.0, 0.54, 1),
#     (107, 'Updating Dictionaries', 1.0, 2.0, 0.53, 1),
#     (107, 'Adding Entries', 1.0, 2.0, 0.52, 1),
#     (107, 'Deleting Dictionaries', 1.0, 2.0, 0.51, 1),
#     (107, 'Merging Dictionaries', 1.0, 2.0, 0.5, 1),
#     (
#     107,
#     'Iterating Through Dictionaries',
#     1.0,
#     2.0,
#     0.49,
#     1
#     ),
#     (107, 'Nested Dictionaries', 1.0, 2.0, 0.48, 1),
#     (107, 'Function Definition', 1.0, 2.0, 0.47, 1),
#     (107, 'Advantages of Functions', 1.0, 2.0, 0.46, 1),
#     (107, 'Executing a Function', 1.0, 2.0, 0.45, 1),
#     (107, 'Default Values', 1.0, 2.0, 0.44, 1),
#     (107, 'Positional Arguments', 1.0, 2.0, 0.43, 1),
#     (
#     107,
#     'Returning Multiple Values',
#     1.0,
#     2.0,
#     0.42,
#     1
#     ),
#     (107, 'Namespace', 1.0, 2.0, 0.41, 1),
#     (107, 'Lambda Functions', 1.0, 2.0, 0.4, 1),
#     (
#     107,
#     'Arbitrary Arguments (*args)',
#     1.0,
#     2.0,
#     0.39,
#     1
#     ),
#     (
#     107,
#     'Keyword Arbitrary Arguments (**kwargs)',
#     1.0,
#     2.0,
#     0.38,
#     1
#     ),
#     (107, 'Classes Definition', 1.0, 2.0, 0.37, 1),
#     (107, 'Objects', 1.0, 2.0, 0.36, 1),
#     (107, 'Methods', 1.0, 2.0, 0.35, 1),
#     (107, 'Instantiating a Class', 1.0, 2.0, 0.34, 1),
#     (107, 'Instance Attributes', 1.0, 2.0, 0.33, 1),
#     (107, 'init method', 1.0, 2.0, 0.32, 1),
#     (107, 'self keyword', 1.0, 2.0, 0.31, 1),
#     (107, 'Code Style', 1.0, 2.0, 0.3, 1),
#     (107, 'Indentation', 1.0, 2.0, 0.29, 1),
#     (107, 'Multi-Line Strings', 1.0, 2.0, 0.28, 1),
#     (107, 'Len Operator', 1.0, 2.0, 0.27, 1),
#     (107, 'Indexing Strings', 1.0, 2.0, 0.26, 1),
#     (107, 'Slicing Strings', 1.0, 2.0, 0.25, 1),
#     (107, 'Looping Through Strings', 1.0, 2.0, 0.24, 1),
#     (107, 'Modifying Case', 1.0, 2.0, 0.23, 1),
#     (107, 'Replacing Characters', 1.0, 2.0, 0.22, 1),
#     (107, 'Concatenating Strings', 1.0, 2.0, 0.21, 1),
#     (107, 'Splitting Strings', 1.0, 2.0, 0.2, 1),
#     (107, 'String Manipulation', 1.0, 2.0, 0.19, 1),
#     (107, 'Indexed Access', 1.0, 2.0, 0.18, 1),
#     (107, 'Escape Sequences', 1.0, 2.0, 0.17, 1),
#     (107, 'In-Place Operations', 1.0, 2.0, 0.16, 1),
#     (107, 'Definition of Arguments', 1.0, 2.0, 0.15, 1),
#     (107, 'Method Usage', 1.0, 2.0, 0.14, 1),
#     (
#     107,
#     'Global and Local Variables',
#     1.0,
#     2.0,
#     0.13,
#     1
#     ),
#     (107, 'LIFO Principles', 1.0, 2.0, 0.12, 1),
#     (107, 'Memory Concepts', 1.0, 2.0, 0.11, 1),
#     (107, 'Matrix Concepts', 1.0, 2.0, 0.1, 1),
#     (107, 'NumPy Definition', 1.0, 2.0, 0.09, 1),
#     (107, 'NumPy.ndarray', 1.0, 2.0, 0.08, 1),
#     (107, 'np.arange()', 1.0, 2.0, 0.07, 1),
#     (107,'Converting from a List to Array',1.0,2.0,0.06,1
#     ),
#     (107, 'Vector Operations', 1.0, 2.0, 0.05, 1),
#     (107, 'Arithmetic Operations', 1.0, 2.0, 0.04, 1),
#     (107, 'Descriptive Statistics', 1.0, 2.0, 0.03, 1),
#     (107, 'Mean in NumPy', 1.0, 2.0, 0.02, 1),
#     (107, 'Median in NumPy', 1.0, 2.0, 0.01, 1),
#     (107, 'Matrices in NumPy', 1.0, 2.0, 0.0, 1)]

#     start_date, end_date = datetime(year=2024, month=8, day=1), datetime(year=2024, month=8, day=30)
#     date_choices = [start_date]

#     while start_date < end_date:
#         # print(start_date)
#         start_date += timedelta(days=2.0)
#         date_choices.append(start_date)

#     values = []
#     for concept in concepts:
#         for _ in range(random.randint(0, 5)):
#             date = random.choice(date_choices)
#             score = concept[4]
#             weight = random.random()
#             test_event = TriggerEventCreate(datetime_stamp=date, student_id=107, concept=concept[1], value=score, weight=weight)
#             values.append(test_event)

#     _populate_table(db, TriggerEvent, values)


def run(db: Session) -> None:
    logger.info("Initializing databases")
    logger.info("Populating database")
    # for fn in [_populate_trigger_events_test]:
    #     fn(db)
    logger.info("Finished populating database")