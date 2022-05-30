from django.shortcuts import render
from django.http import HttpResponse
from .forms import NameForm

from nltk import word_tokenize, ngrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import jaccard_score
import pandas as pd

import numpy as np
import textdistance
import re
from collections import Counter

import json

def final_score(similar_words, input_word):

    phonex_weight = 0.5
    technique_weight = 0.5

    phonics_mistakes = json.load(open("dyslexic_keyboard/phonics_mistakes.txt"))
    shape_mistakes = json.load(open("dyslexic_keyboard/shapes_mistakes.txt"))
    user_mistakes = json.load(open("dyslexic_keyboard/user_mistakes.txt"))

    similar_words_data_score = {}
  
    for similar_word in similar_words:
        counter = 0
        word_score = 0
        for alphabet in similar_word[0]:
            if counter < len(similar_word[0])-1 and counter < len(input_word)-1:
                if alphabet == input_word[counter]:
                    word_score+=1
                
                elif input_word[counter] in user_mistakes or input_word[counter] in shape_mistakes or input_word[counter] in phonics_mistakes:
                
                    if input_word[counter] in user_mistakes:
                        if alphabet in user_mistakes[input_word[counter]]:
                            word_score+= user_mistakes[input_word[counter]][alphabet]
                    if input_word[counter] in shape_mistakes:
                        if alphabet in shape_mistakes[input_word[counter]]:
                            word_score+= shape_mistakes[input_word[counter]][alphabet]
                    if input_word[counter] in phonics_mistakes:
                        if alphabet in phonics_mistakes[input_word[counter]]:
                            word_score+= phonics_mistakes[input_word[counter]][alphabet]

        counter+=1
        
        if len(input_word) == len(similar_word[0]):
            word_score+=1
            phoenix_score_total = word_score/len(alphabet)

            similar_words_data_score[similar_word[0]]= (phoenix_score_total*phonex_weight) + (similar_word[1]*technique_weight)

    top_similar_words = list(dict(sorted(similar_words_data_score.items(), key=lambda item: item[1], reverse=True)).items())[:5]
    return top_similar_words


def my_autocorrect(input_word):
    my_file = open("dyslexic_keyboard/urdu_lughat_list_final.txt", "r")
    content = my_file.read()
    urdu_lughat_list = content.split("\n")

    input_word = input_word.lower()
    
    if input_word in urdu_lughat_list:
        return('Your word seems to be correct')
    else:
        similarities = [1-(textdistance.Jaccard(qval=2).distance(v,input_word)) for v in urdu_lughat_list]
        return(similarities)

def get_eucledian_similar_words(input_word):

    my_file = open("dyslexic_keyboard/urdu_lughat_list_final.txt", "r")
    content = my_file.read()
    urdu_lughat_list = content.split("\n")

    glove_result = my_autocorrect(input_word)

    counter = 0
    similar_words = []
    for similarity in glove_result:
        
        if similarity > 0.0:
        
            similar_words.append((urdu_lughat_list[counter],similarity))
        # print (urdu_lughat_list[counter], similarity)
        counter+=1

    return similar_words

def n_gram_score(input_word, urdu_lughat_list):
    input_word_bigram_list = []

    word_bigrams = ngrams(input_word, 2)

    for grams in word_bigrams:
        input_word_bigram_list.append(grams)

    urdu_lughat_bigrams = []
    for words in urdu_lughat_list:
        urdu_lughat_bigrams.append(ngrams(words, 2))

    n_grams_score = []

    for word_bigram in urdu_lughat_bigrams:
        union = 0
        common = 0

        word_bigram_list = []
        # word_bigrams = ngrams(input_word, 2)
        for urdu_lughat_grams in word_bigram:
            word_bigram_list.append(urdu_lughat_grams) # To check length of urdu lughat word bigram
            
            if urdu_lughat_grams in input_word_bigram_list:
                common+=1
                union+=1
            else:
                union+=1

    diff = abs(len(word_bigram_list)-len(input_word_bigram_list))
    union = union+diff
    n_gram_coffecient = common / union

    n_grams_score.append(n_gram_coffecient)

    bigram_similar_words = []
    counter = 0
    for bigram_similarity in n_grams_score:

        if bigram_similarity > 0.0:
            
            bigram_similar_words.append((urdu_lughat_list[counter],bigram_similarity))
            # print (urdu_lughat_list[counter], similarity)
        counter+=1

    return bigram_similar_words

def processing(user_input_word):
    my_file = open("dyslexic_keyboard/urdu_lughat_list_final.txt", "r")
    content = my_file.read()
    urdu_lughat_list = content.split("\n")

    

    user_input_word = user_input_word

   

    if user_input_word in urdu_lughat_list:
        return "correct"
        
    else:

        bigram_words = n_gram_score(user_input_word, urdu_lughat_list)
        words_bigram_score_final = final_score(bigram_words, user_input_word)

        eucledian_similar_words = get_eucledian_similar_words(user_input_word)
        eucledian_top_words = final_score(eucledian_similar_words, user_input_word)

        final_words = words_bigram_score_final + eucledian_top_words

        top_words = list(dict(sorted(final_words, key=lambda item: item[1], reverse=True)).items())[:3]
        output_words = [x[0] for x in top_words]

        return output_words
        # print(output_words)

def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data['your_name'])
            suggestions = processing(form.cleaned_data['your_name'])
            if suggestions == 'correct':

                print(form.cleaned_data)
                return render(request, 'dyslexic_keyboard/index.html', {'form': form})
            else:

            # form.cleaned_data['suggestion1'] = 'hamza'
                print ( "here", suggestions[0] )
                return render(request, 'dyslexic_keyboard/index.html', {'form': form, 
                'suggestion1':suggestions[0],
                'suggestion2':suggestions[1],
                'suggestion3':suggestions[2]})
           
    else:
        form = NameForm()

    return render(request, 'dyslexic_keyboard/index.html', {'form': form})

    
