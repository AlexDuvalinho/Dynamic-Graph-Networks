**_Extracting Social Networks
from Literary Fiction, Proceedings of ACL 2010, Uppsala, Sweden._**
- objectives of the paper's author is to test whether there is 
`a significant difference in the
nineteenth-century novel’s representation of
social interaction is geographical: novels set
in urban environments depict a complex but
loose social network, in which numerous
characters share little conversational interaction,
while novels set in rural environments
inhabit more tightly bound social networks,
with fewer characters sharing much more
conversational interaction.`
- very interresting technics to extract the graph 
- apply clustering on entities to solve issue of coreference
- detect text dialogue paragraph 
- original idea : weight the edge not only by the number of time two entietes
appears together but also by the the lenght of dialogue between these two characters
`We empirically determined that
the most accurate definition of “adjacency” is one
where the two characters’ quotes fall within 300
words of one another with no attributed quotes in
between. When such an adjacency is found, the
length of the quote is added to the edge weight,
under the hypothesis that the significance of the relationship
between two individuals is proportional
to the length of the dialogue that they exchange.`
- study some property of novels that are written at the first person :
`Not surprisingly, the most
oft-repeated named entity in the text is I, referring
to the narrator. More surprising is the lack of conversation
connections between the auxiliary characters. `

**_Trilcke P., Fischer F., Göbel M., Kampkaspar D. (2015b), Comedy vs. Tragedy: Network
Values by Genre. Network Analysis of Dramatic Texts_**, available at: https://
dlina.github.io/Network-Values-by-Genre/
- Study difference of network based on genre (tragedy, comedy, etc) and century 
- not a detailed analysis (it is not a paper but rather a blog post)
- just some plot like xmean degree vs genre; etc 

**_Segel, E., & Heer, J. (2010). Narrative visualization: telling stories with data. IEEE_**
- not relevant for our purpose : just try to demonstrate that is easier to learn from visual data rather than text

**_Extracting Character Ne tworks
to Explore Literary Plot Dynamics_**
- only focus on Tolstoy's War and Peace
- some graph create by hand ? 
- study evolution on the network between chapter (diff between "War" chapter and "Peace" chapter)

**_Network of Thrones_**
- Only study one book of Game of Thrones
- Apply communities detection 
- Apply centrality measures to detect main characters
- Rank character importances based on some node proporties 
- Edge between two characters if it appears in the same 15-words winwods 

**_How to Tell Stories with Networks: Exploring the
Narrative Affordances of Graphs with the Iliad_**
- concept of "narrative network analysis”
- only focus on the Iliad 
- to produce nice vizualisation, they use force-vector spatialization . `To place our nodes in the
space, we used an algorithm that simulates a system of physical forces: nodes repulse
each other, while edges act as springs attracting the nodes that they connect`

**_Extraction and Analysis of Fictional Character Networks:
A Survey_**
- summary of different technics to extract network :
    1. detect character occurences
    2. unify occurences (say that often nobody do that) 
    `characters occurrences appear under three forms
in text: proper nouns, nominals, and pronouns. Unifying these occurrences can be considered as
a specific version of the coreference resolution problem, which consists in identifying sequences
of expressions, called coreference chain`
    3. interaction detection : 
        - use co-occurence but : `co-occurrence is only a proxy for actual interaction`
    . Need to choose a narrative unit (sentence, 10 sentences, pages, etc)
        - dialogue detection (quote detection)
        - direct action detection 
    4. graph interaction :
        - most of the time "static network" `the interactions between the characters for the period of time corresponding to the
whole narrative.`
        - Dynamic Networks. Most of the time, temporal windows in the chapter. 
        Idea for vizualisation : first plot the all network as a shadow then plot for each slide abode this shadow network 
        
        `Dynamic Networks. Many authors using character networks to solve higher-level problems
identify the dynamics of the story as a very important aspect to be taken into account.
especially true in long-term narratives such as TV or novel series, in which relationships and
characters are likely to change over time. (...) Yet, the overwhelming majority of methods proposed in
the literature rely on static networks. This may be because extracting dynamic networks requires
making tough methodological choices such as choosing the size of the temporal window. Moreover,
time can be modeled in several ways in a network`
- also talk about extract character networks from movies (so cool ! we can quote that)
- then talk about how such graph can be used to perform some analysis on novel 
(almost everybody use the metrics we have seen in classe)   :
    - for instance: classification task :` One can suppose that the social network of characters
corresponding to a work of fiction depends on a number of factors.`
        - most of the case : use supervised approach with handcraft features
        - but can use also unsupervised algorithm with clustering  ?
    - recommendation system based on such network  
    - obtain additional information from a novel 
    - network simplification 
    - Generation and prediction of narratives.
    - story segmentation 
    - role detection 

TOTALEMENT D'ACCORD AVEC ÇA  :
`Another improvement would be to use representation learning instead of manually selecting discriminant
features. This could be performed by using graph embeddings [65], a recent transposition to graphs
of the NLP concept of word embeddings [48]`

**_Genre classification on German novels_**
- classic supervised classification tasks 
- `Overall, we categorize these facets and
their corresponding features into three categories: features
based on stylometrics ([3], [4], [5]), features based on content,
and features based on social networks ([13], [6]), aiming to
cover “human experience” [11] as completely as possible.`
- Only handcraf feature


**_Telling stories about Dynamic Networks with Graphs comics 
from HAL (2016)_**

Details different visualisation techniques to express temporal changes in a dynamic network as clearly as possible, via graphs. Mainly good for ideas provided.
- Reference to surveys 8, 29, 4, 6, 39 that review 100 visu techniques
- Challenges faced: characters identification, depict changes, order of events, spatial context, number of elements (big)
- Representation of changes (marking event in the book's plot): before/after state, abstract metrics (charts and specific metrics about for instance density of the graph or diameter or centrality)
- Temporality changes: think about how to show changes happening in parallel, flash back...  
- Element identity: preserve position of nodes in the graph, same colors... Visual empahsis for main, supporting and extra characters. 
- Overview and detail: part of the graph is highlighted, focus on a subgraph, zoom transition... 
- Representation: size for node, width for edges, lightness to indicate density in groups


**_Structure based clustering on novels_**

Builds social networks from novel to quantify their plot and structure. Performs clustering on the vector of features characterising the novel graph and investigate genre and author.
In other words, create static and dynamic character networks and extract features to perform clustering on genre and authors. 
`INTERESTING PAPER` ! 
- Stanford NER + FilteredNER (improves perf character reco and resolution)
- Co-references: python-nameparser (Title+Firsname+Lastname)+ gender assignation + matching algo (combinations of title, FN, LN; nicknames, most_common¨match)
- Network construction: relation between 2 nodes based on co-occurences and/or conversations. Networkx and Grephi to visu them. 
- Dynamic networks: sequence of static networks, or network with a time axis. 
- Unique survey so created their dataset from gutenberg (238 novels). Grouped novels into 11 genres (3 of them are super closed). Spark NOtes, Shmoop to annotate data. Novel = max of 3 genres
- Features: static like graph density, clustering coef, diameter, central/isolate nodes proportion, male character prop, weight of biggest and second biggest node... Dynamic: presence of character throughout novel, varying prop of characters early stage/end stage...
- Clustering via 'Weka EM'. 27 features for author, 55 for genre. 
- Evalutation via purity, entropy, F1 measure
- See discussion for the results, similar structure for some genre (1 strong character, prop of isolated nodes, disconnected components...)
- Many interesting patterns for author clustering, often related to style pattern (many characters at beginning, connections,...) Dynamic features are important! Pb: changes in author's style across books.
- Look at some groups of books like Harry Potter, Lord of the Rings and study plot evolution. 



- Il faudra aussi citer article sur les graphs embeddings  