import os
from langchain.prompts import PromptTemplate
from langchain_core.prompts import FewShotPromptTemplate

from langchain_openai import OpenAI
from langchain_core.documents import Document

from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chains.llm import LLMChain

from .custom.combine_json import CombineJSONDocsChain
from .custom.map_reduce_extended import MRDExtended

from typing import List


async def concept_id_chain(
        documents: List[Document], 
        subjects: str, 
        course_summary: str, 
        is_enriched:bool=False,
        extra_params:dict={}
        ):
    api_key = os.getenv('TRITON_API_KEY')

    llm = OpenAI(base_url="https://traip13.dsmlp.ucsd.edu/v1", model="llama-3", api_key=api_key, max_tokens=3000, temperature=0.0)
    document_variable_name = "context"

    prefix_prompt = """You are a bot who is a subject matter expert in the following subject(s): "{subjects}"; 
You are identify concepts on behalf of students and staff belonging to a university course with the following course summary: "{course_summary}"; 
A concept is a single, focused idea or notion essential to a course's subject matter and contents, 
representing one discrete topic a student must understand. It is defined by a clear, concise, and descriptive name that conveys its specific meaning and purpose in the curriculum.
Each concept must include: The name of each concept which must not exceed 4 words; The subject the concept belongs to; The difficulty involved to learn the concept, this is on a scale of 1 to 10 where 1 is extremely easy, and 10 is extremely difficult; A 1 to 3 sentence summary describing what the concept is;
Here are some example concepts:"{context_concepts}";
Return nothing else except for an array of JSON objects representing concepts that conforms to the following structure:
[{{'naPme': string, 'subject': string, 'difficulty': integer, 'summary': string}}]"""

    suffix_prompt = """Task: Identify all concepts taught in the following section of course materials: "{context}";"""
    
    example_prompt = PromptTemplate.from_template("Task: {task}\n\n{result}")
    mapping_examples = [
        {
            "task": """Identify all concepts taught in the following section of course materials:"Solve Equations Using the Subtraction and Addition Properties of Equality We are going to use a model to clarify the process of solving an equation.An envelope represents the variable – since its contents are unknown – and each counter represents one. We will set out one envelope and some counters on our workspace, as shown in Figure 2.2. Both sides of the workspace have the same number of counters, but some counters are “hidden” in the envelope. Can you tell how many counters are in the envelope? Figure 2.2 The illustration shows a model of an equation with one variable. On the left side of the workspace is an unknown (envelope) and three counters, while on the right side of the workspace are eight counters. What are you thinking? What steps are you taking in your mind to figure out how many counters are in the envelope? Perhaps you are thinking: “I need to remove the 3 counters at the bottom left to get the envelope by itself. The 3 counters on the left can be matched with 3 on the right and so I can take them away from both sides. That leaves five on the right—so there must be 5 counters in the envelope.” See Figure 2.3 for an illustration of this process. Figure 2.3 The illustration shows a model for solving an equation with one variable. On both sides of the workspace remove three counters, leaving only the unknown (envelope) and five counters on the right side. The unknown is equal to five counters. What algebraic equation would match this situation? In Figure 2.4 each side of the workspace represents an expression and the center line takes the place of the equal sign. We will call the contents of the envelope . Figure 2.4 The illustration shows a model for the equation . Let’s write algebraically the steps we took to discover how many counters were in the envelope: First, we took away three from each side. Then we were left with five. Check: Five in the envelope plus three more does equal eight! Our model has given us an idea of what we need to do to solve one kind of equation. The goal is to isolate the variable by itself on one side of the equation. To solve equations such as these mathematically, we use the Subtraction Property of Equality. 2.1 • Solve Equations Using the Subtraction and Addition Properties of Equality 191 Subtraction Property of Equality For any numbers a, b, and c, When you subtract the same quantity from both sides of an equation, you still have equality. MANIPULATIVE MATHEMATICS Doing the Manipulative Mathematics activity “Subtraction Property of Equality” will help you develop a better understanding of how to solve equations by using the Subtraction Property of Equality. Let’s see how to use this property to solve an equation. Remember, the goal is to isolate the variable on one side of the equation. And we check our solutions by substituting the value into the equation to make sure we have a true statement. EXAMPLE 2.2 Solve: Solution To get y by itself, we will undo the addition of 37 by using the Subtraction Property of Equality. Subtract 37 from each side to ‘undo’ the addition. Simplify. Check: Substitute Since makes a true statement, we have the solution to this equation. TRY IT 2.3 Solve: . TRY IT 2.4 Solve: . What happens when an equation has a number subtracted from the variable, as in the equation ? We use another property of equations to solve equations where a number is subtracted from the variable. We want to isolate the variable, so to ‘undo’ the subtraction we will add the number to both sides. We use the Addition Property of Equality. Addition Property of Equality For any numbers a, b, and c, 192 2 • Solving Linear Equations and Inequalities Access for free at openstax.org When you add the same quantity to both sides of an equation, you still have equality. In Example 2.2, 37 was added to the y and so we subtracted 37 to ‘undo’ the addition. In Example 2.3, we will need to ‘undo’ subtraction by using the Addition Property of Equality. EXAMPLE 2.3 Solve: Solution Add 28 to each side to ‘undo’ the subtraction. Simplify. Check: Substitute The solution to is TRY IT 2.5 Solve: TRY IT 2.6 Solve: EXAMPLE 2.4 Solve: Solution Use the Addition Property of Equality. Find the LCD to add the fractions on the right. Simplify. Check: 2.1 • Solve Equations Using the Subtraction and Addition Properties of Equality 193 Substitute Subtract. Simplify. The solution to is TRY IT 2.7 Solve: TRY IT 2.8 Solve: The next example will be an equation with decimals. EXAMPLE 2.5 Solve: Solution Use the Addition Property of Equality. Add. Check: Let . TRY IT 2.9 Solve: TRY IT 2.10 Solve: Solve Equations That Require Simplification In the previous examples, we were able to isolate the variable with just one operation. Most of the equations we encounter in algebra will take more steps to solve. Usually, we will need to simplify one or both sides of an equation before using the Subtraction or Addition Properties of Equality. You should always simplify as much as possible before you try to isolate the variable. Remember that to simplify an expression means to do all the operations in the expression. Simplify one side of the equation at a time. Note that simplification is different from the process used to solve an equation in which we apply an operation to both sides. 194 2";""",
            "result": """[{{"name": "Subtraction Property of Equality","subject": "Algebra","difficulty": 2,"summary": "Understanding how subtracting the same value from both sides of an equation maintains equality."}},{{"name": "Addition Property of Equality","subject": "Algebra","difficulty": 2,"summary": "Understanding how adding the same value to both sides of an equation maintains equality."}},{{"name": "Isolating the Variable","subject": "Algebra","difficulty": 3,"summary": "Learning to isolate the variable by undoing addition or subtraction to solve for the variable's value."}},{{"name": "Solving Equations with One Operation","subject": "Algebra","difficulty": 3,"summary": "Applying either addition or subtraction to isolate the variable in simple linear equations."}},{{"name": "Manipulative Mathematics: Subtraction Property of Equality","subject": "Algebra","difficulty": 2,"summary": "Using manipulatives (like counters) to visualize and understand the Subtraction Property of Equality."}},{{"name": "Checking Solutions","subject": "Algebra","difficulty": 2,"summary": "Verifying solutions by substituting values back into the equation to confirm equality."}},{{"name": "Solving Equations with Addition and Subtraction","subject": "Algebra","difficulty": 3,"summary": "Using both addition and subtraction to solve linear equations by isolating variables."}},{{"name": "Solving Equations with Decimals","subject": "Algebra","difficulty": 4,"summary": "Using addition and subtraction properties of equality to solve equations containing decimal numbers."}},{{"name": "Simplifying Expressions in Equations","subject": "Algebra","difficulty": 4,"summary": "Breaking down expressions on each side of an equation to simplify before isolating the variable."}},{{"name": "Solving Equations That Require Multiple Steps","subject": "Algebra","difficulty": 4,"summary": "Learning to solve equations by simplifying each side and applying addition or subtraction to isolate variables."}}]"""
        }
    ]
    
    prompt = FewShotPromptTemplate(
        example_prompt=example_prompt,
        examples=mapping_examples,
        suffix=suffix_prompt,
        prefix=prefix_prompt,
        input_variables=["context", "subject", "course_summary", "context_concepts"]
    )

    mapping_chain = LLMChain(llm=llm, prompt=prompt, verbose=True, tags=["mapping-chain"])

    combine_documents_chain = CombineJSONDocsChain(name="name")
    
    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
        verbose=True,
        tags=["reduce-docs-chain"],
        collapse_max_retries=10
    )

    chain = MRDExtended(
        llm_chain=mapping_chain,
        document_variable_name=document_variable_name,
        reduce_documents_chain=reduce_documents_chain,
        verbose=True,
        tags=["map-reduce-docs-chain"],
        additional_doc_vars=["context_concepts"]
    )

    from langchain_community.callbacks import get_openai_callback

    with get_openai_callback() as cb:
        results = await chain.ainvoke({"input_documents": documents, "subjects": subjects, "course_summary": course_summary})

    print(f"\n\nTOKEN COUNT: {cb.total_tokens}\n\n")

    return results
