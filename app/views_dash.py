import numpy as np
from owlready2 import *
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch
import re
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.conf.urls.static import static
import os
import joblib
import gtts
from playsound import playsound

@login_required(login_url="/login/")
def index(request):
    
    context = {}
    context['segment'] = 'form'

    #html_template = loader.get_template( 'form.html' )
    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. A
    # nd load that template.

        
    load_template      = request.path.split('/')[-1] 
    context['segment'] = load_template
        
    html_template = loader.get_template( load_template )
    return HttpResponse(html_template.render(context, request))


def upload (request):    
        
    return render(request, 'ui-typography.html')


onto = get_ontology('out.owl')

onto.load()

classes = list(())
properties = list(())
individuals = list(())

for item in onto.classes():
    classes.append(item)
for item in onto.properties():
    properties.append(item)
for item in onto.individuals():
    individuals.append(item)



all= []
for item in onto.classes():
  if len(list(item.descendants(include_self = False)))!=0:
    all.append(item)
for item in classes:
    for i in list(item.descendants(include_self = False)):
      all.append(i)
for item in individuals:
  all.append(item)




df = pd.DataFrame(all, columns =['paths'])

#remove all punctuation like '? ! ; ..'
import string 
def remove_punctuation(text):
    txt_nopunct= ''.join([c for c in text if c not in string.punctuation])
    return txt_nopunct


df['noun phrases'] = df['paths'].apply(lambda x:re.sub(r"out", "", str(x)))
df['noun phrases'] = df['noun phrases'].apply(lambda x:re.sub(r"[0-9]", "", x))
df['noun phrases'] = df['noun phrases'].apply(lambda x:re.sub(r"_", " ", x))
df['noun phrases'] = df['noun phrases'].apply(lambda x:re.sub(r"\\n", " ", x))
df['noun phrases'] = df['noun phrases'].apply(lambda x:re.sub(r"\n", " ", x))
df['noun phrases'] = df['noun phrases'].apply(lambda x:re.sub(r"\\n", " ", x))



df['noun phrases'] = df['noun phrases'].apply(lambda x:remove_punctuation(x))



def result(request):
    query_sentence=request.GET['query_sentence']

    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    corpus_embeddings = model.encode(df['noun phrases'].values, convert_to_tensor=True)
    query_embedding = model.encode(query_sentence, convert_to_tensor=True)

# We use cosine-similarity and torch.topk to find the highest 3 scores
    cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = torch.topk(cos_scores, k=1)



    for score, idx in zip(top_results[0], top_results[1]):
        score = score.cpu().data.numpy() 
        idx = idx.cpu().data.numpy()
        concept_name=df['noun phrases'].iloc[idx]
        if df['paths'].iloc[idx].isDefinedBy[0] not in [""," ","  ","   "]:
           definition=df['paths'].iloc[idx].isDefinedBy
           tts = gtts.gTTS(str(definition))
           tts.save("definition.mp3")

           print(type(definition))
        if len(list(df['paths'].iloc[idx].descendants(include_self = False))) !=0:
           sous_concept=df['paths'].iloc[idx].descendants(include_self = False)
        else:
           sous_concept=df['paths'].iloc[idx].instances()


    return render(request,'result.html',{'concept_name':concept_name,'definition':definition,'sous_concept':sous_concept})
