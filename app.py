from flask import Flask
import spacy
import random,json,re
import numpy as np
import pandas as pd
import PyDictionary

dictionary=PyDictionary.PyDictionary()
nlp = spacy.load('en')

header_text = '''


<script src='https://code.jquery.com/jquery-2.1.4.js'></script>

<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js" integrity="sha384-0mSbJDEHialfmuBBQP6A4Qrprq5OVfW37PRR3j5ELqxss1yVqOtnepnHVP9aJ7xS" crossorigin="anonymous"></script>


<script>
        var margin = {
            top: 20,
            right: 20,
            bottom: 300,
            left: 20
        };

        var w = window,
            d = document,
            e = d.documentElement,
            g = d.getElementsByTagName('body')[0],
            width = w.innerWidth || e.clientWidth || g.clientWidth,
            height = w.innerHeight || e.clientHeight || g.clientHeight;

        width = width - margin.left - margin.right,
            height = height -margin.top-margin.bottom;

    var transform = function()
    {
    console.log('Transforming...')

    console.log($('#input').val());

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/blur/"+encodeURIComponent($('#input').val()), false);
    xhr.send();

    console.log(xhr.status);
    console.log(xhr.statusText);
    console.log(JSON.parse(xhr.response))

    var transformedText=JSON.parse(xhr.response)['transformed'];

    document.getElementById('output-div').innerHTML = '<b>Unplaigiarised text: </b>'+transformedText;

    var makeList=function(e1,e2)
    {return '['+e1+','+e2+']';}

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/sim/", false);
    xhr.send();

    document.getElementById('sim-div').innerHTML = xhr.response;
    }

</script>
<div class="container">

  <div class="well">
  <div class="media">
  <h4>Let's blur some text!
  </h4>
  </div>
  </div>

<div class="row">
    <div class="input-group">
      <input onsubmit="transform()" id="input" name="input" type="text" class="form-control" placeholder="Search for..." value="The quick brown fox jumps over the lazy dog">
      <span class="input-group-btn">
      <button class="btn btn-primary" id="submitText" style=" width:100%" onclick=transform()>Plaigiarise!</button>
        </span>
    </div><!-- /input-group -->
  </div><!-- /.col-lg-6 -->
<br>
<div class="row">
<div id="output-div">
</div>

<br>
<div class="row">
<div id="sim-div">
</div>


</div>

<head> <title>Blurring Plaigiarism</title> </head>
</div>
'''

def getSymPy(word,p=0.1):
    if random.random()>p:
        print 'unchanged'
        return word
    else:
        syns=dictionary.synonym(word)
        if syns>0:
            return random.choice(syns)
        else:
            return word

def scrapeText(url):
    return json.dumps({'transformed':'<Scrape URL here>'})

def transformText(text):

    print 'Transforimg...'

    if re.search(r'www\|http',text):
        print 'Its a URl'
        text=scrapeText(text)

    doc=nlp(text)

    global df
    df=pd.DataFrame(data={'text':[tok.text for tok in doc],'pos':[tok.pos_ for tok in doc]})

    ## Transform text
    df['transformedText']=df.apply(lambda row: getSymPy(row['text'],p=1.)\
        if row['pos'] in ['ADV','ADJ'] else row['text'],axis=1)

    df['isTransformed']=~(df['text']==df['transformedText'])

    htmlStringTransformed=' '.join(df.apply(lambda x:'<mark>%s</mark>' % x['transformedText'] if x['isTransformed']\
         else x['transformedText'],axis=1))

    global originalString
    originalString=' '.join(df['text'])
    global transformedString
    transformedString=' '.join(df['transformedText'])

    return json.dumps({'transformed':htmlStringTransformed.capitalize()})

def jaccard(x,y):
    x=x.split(' ')
    y=y.split(' ')
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality/float(union_cardinality)

def getSim():
    print transformedString
    print originalString

    return '%d%%' % (100*jaccard(transformedString,originalString))

application = Flask(__name__)

application.add_url_rule('/', 'index', (lambda: header_text),methods=['GET', 'POST'])
# Index page

application.add_url_rule('/blur/<text>','blur',transformText,methods=['GET','POST'])

application.add_url_rule('/sim/','sim',getSim,methods=['GET','POST'])


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
