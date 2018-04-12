# FinalYearProject
Collection of Scripts, files and documents for my Final Year Btech project on information flow through social networks (like twitter).

Final Result:

<p align="center"><img src="https://i.imgur.com/OMZ2VCT.png" /></p>
Here we searched for tweets for the hashtag #fakenews around begining of April when the Indian IB Ministry had issued a circular regarding punishing journalists who spread fake news. We were able to scrape tweets and find distinct clusters of twitter accounts who were talking about this using hashtag #fakenews <br/>

Orange = BJP inclined accounts<br/>
Blue = Congress inclined accounts<br/>
Green = News outlets and mostly unbiased accounts<br/>
Purple = Accounts from USA who were talking about the media targetting Trump with #fakenews<br/>


v1.0 - contains the initial presentation and report that was created after the initial study, also contains the first program I wrote to draw the graph using twitter accounts and the list of their followers, following. The program took a list of accounts as input. 
I was using an online tool to grab tweets from #hashtags on twitter then extracting the accounts which tweeted to make the list of nodes for this program. 


v2.0 - a complete standalone program to just accept a #hashtag. It will then extract tweets, retweets and graw graph using both the details.

v2.5 - the program can now also export the edge list in .gexf format so that it can be imported to Gephi. The program when run with "resolve" command will convert the node names from twitter account IDs to usernames. The program now has multiple checkpoints so that even if the program crashes during any of the steps we can restart from the same point.


