## Context

This project has been realized for the Network Science Analytics class (MSc AI 2019-2020 at CentraleSupelec) by :

- Gaël de Léséleuc
- Alexandre Duval 

The aim of our project was to conceive a pipeline that would extract a dynamic narrative graph from a given novels and then used this graph to study the narrative story of the novel. 
A detailed report can be found in the *Report* folder. 

## Installation 

To install and use our end-to-end processing pipeline : from novel to narrative graph,  use the following command in a new environment. 

```
git clone https://github.com/dldk-gael/novel_story_building.git
cd novel_story_building 
pip install -r requirements.txt
```

Our pipeline use BERT-NER in order to recognize the character names in the text. As a result, if you want to use it, you must  [download](https://1drv.ms/u/s!Auc3VRul9wo5hghurzE47bTRyUeR?e=08seO3) the weight of pre-trained BERT-NER model and save it in the *models* folder. 

Note that we have upload some cache data in the *data* folder so that you can test our pipeline without having to preprocess raw data from scratch.

## Pipeline structure

The folder has the following organization : 

- *models* : to store the weight of BERT-NER model
- *data*: to store the data
  - *raw_text* : **put here the novel.txt you want to analyse**
  - *book_by_chapter* : will contain the novel split by chapter 
  - *coref_rules* : contains database that are use by coreference rules module 
  - *entity_list* : will contain the output of text processing as pickle file (ie: the occurence list)
  - *graph* : will contain the narrative graph 
- *report*: contains the project assignment description, our project proposal, our project report
- *src* is divide in three modules :
  - *third_party* : contains source code of other frameworks we used such as BERT-NER and chapterize
  - *text_processing* : the module responsible of text processing
  - *graph* : the module responsible of graph creation and graph analysis  

## Utilisation

To process a book and obtain different narrative graph as .gexf files, store the file book_name.txt in data/raw_test/ and launch the command : 

```
python main.py --book book_name 
```

By default, if you launch :

```
python main.py
```

it will re-run some graph analysis on HarryPotter book using cache data we left in the data folder. 