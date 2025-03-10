LEARN_CHARACTERS_PROMPT_TEMPLATE = """

You will be given 5 words in pinyin and some information about chinese characters. 

First: translate the pinyin word to chinese characters.
Second: use the given context to give a short explanation of the character's meaning and how to easily remember the character.

{pinyin_words}
{context}

Format your output using the following guidelines:
1. pinyin word: characters and explanation
2. pinyin word: characters and explanation
3. pinyin word: characters and explanation
4. pinyin word: characters and explanation
5. pinyin word: characters and explanation

Only provide information about the five pinyin words provided to you. 

Give multiple new lines between each pinyin word and its corresponding character explanation to ensure good formatting.
"""