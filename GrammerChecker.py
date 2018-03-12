#Grammer Checker
#I check for their/there grammer mistakes and makes corrections. Trust me, I was programmed to do this.
#https://twitter.com/grammer_checker
#(Essay in post-script)
from stat_parser import Parser
import regex as re    
import string
import nltk
from nltk import word_tokenize, pos_tag
import tweepy
import random
from nltk import Tree

#Copyright 2018 Adriaan Odendaal
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#twitter keys
consumerKey = #Omitted
consumerSecret = #Omitted
accessToken = #Omitted
accessTokenSecret = #Omitted
auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(auth) 

def encoder(tweet):
  encoding=tweet.text
  encoded=encoding.encode("ascii","ignore")
  return encoded 

def searchTweets(keyword, counter):
  print '**Selecting Tweet**','\n'
  print 'Keyword: ', keyword
  searchResults = api.search(q = "\""+keyword+"\"")
  selectedTweet = searchResults[-1]
  counter = counter+len(searchResults)*(-1)
  #print dir(selectedTweet) #All the attributes of selected tweet 
  #print 'Selected tweet: ','\n',selectedTweet.created_at, '\n', selectedTweet.user.screen_name, '\n', selectedTweet.text.encode('utf-8')#Not neccesary, but keeps it unicode so that python doesn't freak out the terminal
  selectedTweet3=encoder(selectedTweet)
    
  #Makes sure it isn't a Retweet (because then the whole reply thing fucks out 
  while selectedTweet3[:2] == 'RT':
    selectedTweet=searchResults[counter]
    selectedTweet3=encoder(selectedTweet)
    counter =counter+1
    print 'RT Found'
  #Makes sure keyword is in the tweet
    while keyword not in selectedTweet3:
      print 'Keyword Not Found'
      selectedTweet=searchResults[counter]
      selectedTweet3=encoder(selectedTweet)
      counter =counter+1
	
  print '*Keyword present*','*Not a RT*'
  print 'Username: ', selectedTweet.user.screen_name
  print 'ID:', selectedTweet.id
  selectedTweetFinal = cutter(selectedTweet3,keyword)
  print 'Selected Tweet Cut for Parsing:', selectedTweetFinal
  return selectedTweetFinal,selectedTweet

def grammerChecker(counter):
  keyword=keywordSelecter()
  sentenceCheck, tweetReply = searchTweets(keyword,counter)
  sentenceCorrected = grammerAlgorithm(sentenceCheck)
  print 'Original: ', sentenceCheck 
  print 'Correction: ', sentenceCorrected
  if sentenceCorrected is not None:
    grammerCorrector(sentenceCorrected, tweetReply)
  else: 
    print 'Sentence not Parsed','\n','**Run Again**'
    grammerChecker (counter+1)
    
def grammerCorrector(sentenceCorrected, tweetReply):
  print '\n','**Replying**','\n'
  #print '\n', tweetReply.text, '\n', tweetReply.user.screen_name,'\n',tweetReply.id
  reply= '@'+tweetReply.user.screen_name+' '+sentenceCorrected
  print 'Reply:' ,reply
  print 'Reply ID:', tweetReply.id
  #print tweetId
  api.update_status(status =reply,in_reply_to_status_id =tweetReply.id)
  
def keywordSelecter():
  keywordsList = ('there','their')
  return keywordsList[random.randint(0,1)]
  
def grammerAlgorithm(sentenceCheck):#Grammer Engine
  print '\n','**Checking Grammer**','\n'
  #This is the grammatical rules according to which my GrammarCheck algorithm will 'chunk' sentences into 'incorrect' phrasal grammatical constructs. The 'incorrect grammar' structure (of course, this is really 'correct', as far as I can tell. I tried looking at the grammar rules concerning 'their' and 'there' but of course, I might be wrong. And if I am wrong, then the software is too. Though, in this case, 'wrong' means 'right', right?):
  grammar = """NounPhrase Their: {<PRP\$>+<JJ>*<DT>*<NN|NNS>} 
  VerbPhrase There:  {<VBG|IN|VBG|VBZ|VBD|VBP>?<EX>|<EX>+<VBG|IN|VBP|VBG|VBZ|VBD>}
  AdverbPhrase There: {<IN>+<RB>}
  EX: {<there>+<EX>}
  RB: {<there>+<RB>}
  PRP\$: {<their>+<PRP\$>}"""
  #Full list of tags: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
  #Tags the words according to the specific library I'm using. 
  sentences = nltk.pos_tag(nltk.word_tokenize(sentenceCheck)) 
  cp = nltk.RegexpParser(grammar) #building the phrasal chunk parser using my grammatical rules
  result = (cp.parse(sentences))#applying the parser to the sentence
  #print 'Sentence parsed: ', result 
  
  grammarCheckMatrix = [['NounPhrase Their','PRP$','Their','their','There','there'],['VerbPhrase There','EX','There','there','Their','their'],['AdverbPhrase There','RB','There','there','Their','their']]
  #The algorithm to checks if the 'incorrect grammar' has been used 
  for x in range(len(grammarCheckMatrix)):
    for child in result:
      if grammarCheckMatrix[x][0] in str(child): #For 'their' instead of 'there'
        #print 'Child: ',child
        #print child.label()
        for childofchild in child:
          if childofchild[1] == grammarCheckMatrix[x][1]:
            if child[0] is grammarCheckMatrix[x][2] or grammarCheckMatrix[x][3]:
            #print 'Childofchild:', childofchild 
              corrected = (sentenceCheck.replace(grammarCheckMatrix[x][2], ('*'+grammarCheckMatrix[x][4]))).replace(grammarCheckMatrix[x][3], ('*'+grammarCheckMatrix[x][5]))
              errorMessage= 'Did you mean: "'+ corrected.strip()+'"?' 
              return errorMessage
        #return correction 
		
def cutter(selectedTweet3,keyword):
  sentence = selectedTweet3
  print 'Selected Tweet: ',sentence
  print '\n', '**Cutting**', '\n'
  keyword = keyword
  print 'Keyword: ', keyword 
  toCut={}
  toCut['before'], keyword, toCut['after'] = sentence.partition(keyword.lower())
  print 'Cuts: ', toCut['before'], 'XCUT HEREX', keyword,'XCUT HEREX', toCut['after']

  for pieces in toCut:
    #regex = re.compile('[%s]' % re.escape(string.punctuation))
    #toCut[pieces] = regex.sub('*CUTHERE*', toCut[pieces])
    toCut[pieces] =re.sub("https","",toCut[pieces])
    toCut[pieces] =re.sub(ur"\p{P}(?<!')", "*CUTHERE*", toCut[pieces])
    #print 'Cut', pieces, 'here :',toCut[pieces]
	
  listerBefore = toCut['before'].split('*CUTHERE*')
  listerAfter = toCut['after'].split('*CUTHERE*')
  print 'Cut before keyword: ',listerBefore
  print 'Cut after keyword: ',listerAfter    
  sentence= (listerBefore[-1]+keyword+listerAfter[0]).replace('  ',' ')
  
  return sentence
  
def main():
 grammerChecker(0)
  
if __name__ == "__main__":
  main()

#Its easy to think of software, especially with the discursive and semiotic veneer of consumer-grade products, as inherently trustworthy. 
#We've gotten used to it: just letting automation do its job. 
#Grammer Checker is a cheeky bot meant to undermines our over-confidence in automated systems as necessarily accurate and utilitarian. 
#This bot is meant to subvert the trust we place in such systems by acting as tactical media.

#Masquerading as just another utilitarian tool, it is in fact explicitly programmed to suggest the wrong corrections - to (un)correct grammar usage of 'there' and 'their' found on Twitter.
#(It would be interesting to see if people assume that the suggestions made are correct just because they comes from an automated system, if they'd momentarily doubt themselves, or whether they would confront the software). 
#Do people place more trust in their own knowledge and intuition than in a software that seemed designed to correct them? 
#Will those (un)corrected by GrammerChek simply turn to the algorithms of Google or Microsoft Word instead to double-check against another software?
#Though in most cases software like Microsoft Word are meticulously engineered to be as close to flawless as possible, I think we have adopted a flawed cultural perception that all software are necessarily so by mere virtue of being shipped as such. 
#Perhaps because source code falls into the same seemingly rigorous systematic codification as spelling and grammar itself we feel there are some immutable laws that make them rigorous. 
#Yet who do we turn to to see if the algorithm of a black-boxed consumer product is 'correct'? 
#(In this case, however, you can read the source-code below and clearly see that the 'grammar' of the grammar-algorithm is incorrect).

#Importantly, the way we conceive of software, and the way software is culturally constructed, are interrelated. 
#Marketing rhetoric, corporate and institutional rubber-stamps, tech-jargon, branding, and an all-round techno-positivism play important roles in what software is as culture. 
#That is also why, importantly, I've dressed up my bot not as the cobbled-together open-source amateur hour project it is - but as a 'real' product. 
#Yet, to avoid Poe's law, the name of the software is itself a clue to the 'flawed design' as well as the Twitter profile pic and (worth the read) banner. 
#For after all, despite my academic pontification, this 'tactical media' machine is little more than a Troll. 
