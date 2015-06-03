raw data
--------

  * conversation_id
  * username
  * timestamp
  * message

enrichment
----------

  * number of links/gif/jpg in message
  * number of words/letters in message
  * list of words present (exluding stopwords and using lemmatization and stemming)

vizualization
-------------

Visualization to browse inside hangout

  * scatter graph with multi filter (user/dow)

Visualization to reveals trends with some nice stats by users.
Profile card template on top of the page with figures/skills(progress bar) for specific users. Users avatar just after for selection

  * skills (main site redirection/café call)
  * rates (vocabulary/fame)
  * record (most long word/most long post/most message in one hour)

Nice statistics examples: 

    data = { date(%Y%m) : nb_events }

  * sparkline of number of event per month
   
    data = { date(%Y%m%d) : nb_events }

  * total number of events
  * max event in one day
  * avg daily number of events
  * total days with at least one event
  * sparkline of number of event per day
    
    data = { datetime(%Y%m%d%H) : nb_events }

  * max event in one hour

    data = { datetime(%Y%m%d%H%M) : nb_event }

  * sparkline avg number of event per minute in a day
  
    data = { time(%H%M%S) : nb_events }

  * max last event
  * min first event
  * avg last event (second conversion)
  * avg min event (second conversion)

    data = [ alias ]

  * list of alias

    data = [ quote ]

  * list of quote

    data = { words : nb_occurence }

  * total number of words (sum nb_occurence)
  * main words (first larger occurence)
  * longuest word used (larger word)
  * total number of unique words (len(data))

    data = [ msg ]

  * longuest message text posted

    data = { date(%Y%m%d) : nb_links }

  * avg daily numbers of links

    data = { username : nb_occurence }

  * total number of self reference

    data = { site : nb_occurence }

  * main site redirection
  * total numbers of links
  

