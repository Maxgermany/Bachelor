import numpy as np
import random
import re
import sys

sys.setrecursionlimit(10000)

def markov():
    path = "../Data/Gameknot/corpusfilterOtherLanguages.txt"

    with open(path, encoding='utf-8') as f:
        text = f.read()

    tokenizedText = [word for word in re.split(' ', text) if word != '']

    markovChains = {}

    for token in list(set(tokenizedText)):
        markovChains[token] = {}

    currentWord = tokenizedText[0].lower()
    for word in tokenizedText[1:]:
        word = word.lower()

        if word not in markovChains[currentWord]:
            markovChains[currentWord][word] = 0

        markovChains[currentWord][word] += 1
        currentWord = word

    limit = 0
    for word in ('the', 'by', 'who', 'game', 'king', 'check', 'pawn', 'mate', 'in', 'brilliant'):
        next_words = list(sorted(markovChains[word], key=markovChains[word].get, reverse=True))[:limit]
        for next_word in next_words:
            print(word, next_word)

    print(generateText(markovChains, 1000))

markov()

def generateText(graph, distance=5, startWord=None):
    if distance <= 0:
        return []

    if not startWord:
        startWord = random.choice(list(graph.keys()))

    weights = np.array(list(graph[startWord].values()), dtype=np.float64)
    weights /= weights.sum()

    choices = list(graph[startWord].keys())
    bestNextWord = np.random.choice(choices, None, p=weights)

    return [bestNextWord] + generateText(graph, distance=distance-1, startWord=bestNextWord)
