import json
from langchain_openai import ChatOpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
from backend.data_models.data_models import Corrections
from langchain_core.prompts import ChatPromptTemplate
from backend.prompts.CorrectionsPrompt import CORRECTIONS_PROMPT_TEMPLATE
import re
from langchain_core.output_parsers import StrOutputParser

from backend.prompts.LearnCharacters import LEARN_CHARACTERS_PROMPT_TEMPLATE

# Load the environment variables
load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)

#
llm = ChatOpenAI(
    model="gpt-4o-mini"
)

def json_parser(response) -> Corrections:
    """
    Parse the JSON response and return a Corrections object.

    Args:
        response: The response object containing JSON data.

    Returns:
        Corrections: The parsed Corrections object.
    """
    json_response = json.loads(response.content)
    return Corrections(**json_response)

async def process_sentence_langchain(sentence: str, language: str) -> Corrections:
    """
    Process a sentence using LangChain and return corrections.

    Args:
        sentence (str): The sentence to process.
        language (str): The target language.

    Returns:
        Corrections: The corrections for the sentence.
    """
    prompts = ChatPromptTemplate.from_messages([
        (
            "system", """You are a foreign language instructor, give corrections in the following form:
                {{
                    "original": "The original text",
                    "corrected": "The corrected text", 
                    "explanation": "Short explanation of grammar mistakes"
                }}"""
        ),
        (
            "user", "{input}"
        )
    ])

    # Give input to prompt template to format
    input = CORRECTIONS_PROMPT_TEMPLATE.format(
        student_response=sentence,
        target_language=language
    )

    # Create a chain to provide the messages to the model, call the model, and parse the output
    chain = prompts | llm | json_parser

    response = chain.invoke(input)

    return response

async def learn_characters(pinyin_words: str, context: str):
    """
    Learn characters based on the provided words and context from Chinese Character pdf.

    Args:
        pinyin_words (str): The pinyin words to learn.
        context (str): The context from the Chinese character pdf for learning the word.

    Returns:
        str: The response with explanations on how to learn some chinese characters.
    """

    prompts = ChatPromptTemplate.from_messages([
        (
            "system", "You are a language instructor"
        ),
        (
            "user", "{input}"
        )
    ])

    input = LEARN_CHARACTERS_PROMPT_TEMPLATE.format(
        pinyin_words=pinyin_words,
        context=context
    )

    chain = prompts | llm | StrOutputParser()

    response = chain.invoke(input)

    return response


# This function is not used anymore
# Previous implementation without using langchain and using OpenAI chat completions
# keeping it here for reference in case I decide to revert back to openai
async def process_sentence_openai(sentence: str, language: str) -> Corrections:
    """
    Process a sentence using OpenAI and return corrections.

    Args:
        sentence (str): The sentence to process.
        language (str): The target language.

    Returns:
        Corrections: The corrections for the sentence.
    """
    prompt = CORRECTIONS_PROMPT_TEMPLATE.format(
        student_response=sentence,
        target_language=language
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": "You extract corrections into JSON data"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format=Corrections
    )

    return completion.choices[0].message.parsed

async def correct_text(message: str, language: str) -> list[Corrections]:
    """
    Asynchonously correct each indiviaual sentence in the given text.

    Args:
        message (str): The message to correct.
        language (str): The target language.

    Returns:
        list[Corrections]: A list of corrections for each sentence.
    """

    # Split the message into sentences
    sentences = re.split(r'[.!?]', message) if re.search(r'[.!?]', message) else [message]

    # Process each sentence in parallel
    tasks = [process_sentence_langchain(sentence.strip(), language) for sentence in sentences if sentence.strip()]
    results = await asyncio.gather(*tasks)

    return [result.model_dump() for result in results]

async def grammar_query(context: str, corrections: str):
    """
    Provide examples of similar mistakes made by the student in the past, given 
    current mistakes and context.

    Args:
        context (str): The context for the query.
        corrections (str): The corrections made by the student

    Returns:
        str: The response from the grammar query.
    """
    prompts = ChatPromptTemplate.from_messages([
        (
            "system", """You are providing similar examples of the student making a grammar mistake.
            
            Look at the list of corrections given and determine whether any of the examples match the student's mistakes. 
            If none of the corrections match the context, return only "No previous similar grammar mistakes found".
            
            Otherwise, provide the examples that match the student's mistakes.""",
        ),
        (
            "user", "{input}"
        )
    ])
    chain = prompts | llm

    response = chain.invoke(context+corrections)

    return response.content