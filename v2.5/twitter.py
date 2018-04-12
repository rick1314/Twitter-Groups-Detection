import tweepy
from time import sleep
import json
import networkx as nx
import matplotlib.pyplot as plt
import sys
from pprint import pprint


#This the time to wait for the rate limit to be cleared
SLEEP_TIME          = 4*1  #60x15
#The name of the file containing the nodes, must be within the same directory
FILE_NAME           = 'nodes.txt'

#You need to create an app to get ACCESS_TOKEN, and ACCESS_SECRET
CONSUMER_KEY        = 'tfamQXljaLWuJnVRivkEYtIly'
CONSUMER_SECRET     = '71ARMeDl18dgV4mVoWlCZlzwusQgpUztTx3VCSL0zSIqcilWvw'
ACCESS_TOKEN        = '983927012803756033-sPvVVQcNuxjillunU9WvRVFNnatey1A'
ACCESS_SECRET       = 'VDPqPLkEYB6LvqNAiz4oGD2ssdmQ9wuDAVHiNagjEOAmM'

#If set to true, the graph will contain an shared friends between nodes, keep in mind
#that this will increase the number of edges in very very large way
FRIENDS_OF_FRIENDS  = False
#consider the list of people follwoing the node
FOLLOWING           = True
#Consider the list of people followed by the node
FOLLOWED            = True
#Use the last generated vertices file
USE_FILE            = False
#Display labels
LABELS              = True

#Dsiplays isolated nodes
ISOLATED            = True

LOAD_PREVIOUS       = True

NO_COL              = True

LOAD_VERTS          = True

#Limit of tweets for a hashtag
TWEETS_LIM   = 10
#Limit of retweets for a tweet
RETWEETS_LIM = 4
#The tag to search
TAG          = '#test2211999'
TYPE         = 'recent'     #Change to popular for large searches
def auth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth, parser=tweepy.parsers.JSONParser())

API = auth()

def retweets(tag=TAG,api=API):
    tweets              = []
    tweets_users        = {}
    retweets_users      = {}

    for x in make_call(api.search,TAG,count=TWEETS_LIM,result_type=TYPE)['statuses'] :
        try :
            tweets.append(x['id'])
            tweets_users[x['id']] = [x['retweeted_status']['user']['id']]
        except :
            pass

    for x in tweets :
        retweets_users[x] = []
        for y in  make_call(api.retweets,x,count=RETWEETS_LIM) :
            retweets_users[x].append(y['user']['id'])

    res = {'tweets_users':tweets_users,'retweets_users':retweets_users}
    with open('rtws.json','w') as f:
        json.dump(res,f)
    return tweets_users,retweets_users

def ids_rt(rt):
    res = []
    for x in rt[0]:
        res+=rt[0][x]
    for x in rt[1]:
        res+=rt[1][x]

    return list(set(res))

def load():
    with open(FILE_NAME) as f :
        res = reversed([x.strip() for x in f.readlines() if x.strip()!=''])
    return res

def make_call(func,*args,**kwargs):
    print('x')
    while True :
        try :
            return func(*args,**kwargs)
        except Exception as e :
            if 'that page does not exist' in str(e):
                return []
            print (e)
            print ('Sleeping for {} seconds'.format(SLEEP_TIME))
            sleep(SLEEP_TIME)

def resolve(names,api=API):
    res = {}
    for name in names :
        res[name] = make_call(api.get_user,name).id
    return res

def followers(ids,api = API):
    #ids =  [ids[x] for x in ids]
    res = {id:{'followed':[],'following':[]} for id in ids}
    if LOAD_PREVIOUS :
        try :
            with open('prev.json') as f:
                res = json.load(f)
        except:
            with open('prev.json','w') as f:
                json.dump(res,f)
    for id in ids:
        if not res.get(str(id)):
            res[str(id)] = {'followed':[],'following':[]}

        if FOLLOWED  and len(res[str(id)]['followed']) == 0:
            print ('Getting followers for : {}'.format(id))
            res[str(id)]['followed'] =  make_call(api.followers_ids,id)
            with open('prev.json','w') as f:
                json.dump(res,f)

        if FOLLOWING  and len(res[str(id)]['following']) == 0 :
            print ('Getting friends for : {}'.format(id))
            res[str(id)]['following'] =  make_call(api.friends_ids,id)
            with open('prev.json','w') as f:
                json.dump(res,f)
    return res

def build_tree(friends_dict,resolved):
    verts = []
    for id in friends_dict :
        print (id)
        if FOLLOWED :
            try :
                for x in friends_dict[id]['followed']['ids']    :
                    if check(id,x,friends_dict):
                        verts.append([long(id),x])
            except :
                pass
        if FOLLOWING :
            try :
                for y in friends_dict[id]['following']['ids']    :
                    if check(id,y,friends_dict):
                        verts.append([long(id),y])
            except :
                pass
    #inv_res = {resolved[x] : x for x in resolved}
    #for x in verts :
    #    if inv_res.get(x[0],False):
    #        x[0] =  inv_res[x[0]]

    #    if inv_res.get(x[1],False):
    #        x[1] =  inv_res[x[1]]
    return verts

def build_tree_tweets(tweets_users,retweets_users,followers_dict):
    verts   = []
    if NO_COL :
        green   = []
        red     = []
        orange  = []
    else :
        red     = list(set( [user[0] for user in tweets_users.values()] ))
        orange  = list(set([ user for users in retweets_users for user in retweets_users[users] ]))
        green   = list(set([x for x in red if x in orange]))


    verts  = build_tree(followers_dict,{})
    with open('verts.json','w') as f:
        json.dump(verts,f)
    #for x in retweets_users :
    #    for user in retweets_users[x]:
    #        if user != tweets_users[x][0]:
    #            verts.append([user,tweets_users[x][0]])


    return red,orange,green,verts

def save_verts(verts,name = 'verts.json'):
    with open(name,'w') as f:
        json.dump(verts,f)

def load_verts(name = 'verts.json'):
    with open('verts.json') as f:
        verts = json.load(f)
    return verts

def check(id,x,friends_dict):
    for y in friends_dict :
        y = long(y)
        id = long(id)
        if y!= id :
            if not FRIENDS_OF_FRIENDS :
                if x == y :
                    return True
            elif x == y or (FOLLOWED and x in friends_dict[y]['followed']) or ( FOLLOWING and x in friends_dict[y]['following'] ) :
                return True
    return False

def get_stats(verts):
    print ('Number of edges : {}'.format(len(verts)))
    flt = [x for y in verts for x in y]
    st = set(flt)
    dgs = list(reversed(sorted([[x,flt.count(x)] for x in st],key = lambda x:x[1])))

    flt = [y[1] for y in dgs]
    st = set(flt)
    for x in st :
        print ('Nodes with degree {} : {}'.format(x,flt.count(x)))
    print ('Average Degree of all nodes : {}'.format(sum(flt)/(len(flt) or 1)))

def graph_retweets(red,orange,green,verts):

    G=nx.Graph()
    G.add_edges_from(verts)
    G.add_nodes_from(red+orange+green)
    color_map = []
    for x in G.nodes() :
        if x in green:
            color_map.append('green')
        elif x in red :
            color_map.append('red')
        else :
            color_map.append('orange')
    get_stats(G.edges())
    nx.draw(G,node_color = color_map,with_labels = LABELS)
    plt.show()

def graph(verts,resolved,friends_dict=None):
    G=nx.Graph()
    if ISOLATED :
        flat = []
        for x in verts :
            flat.append(str(x[0]))
            flat.append(str(x[1]))
        flat = set(flat)
        G.add_nodes_from([x for x in resolved if str(x) not in flat])
    G.add_edges_from(verts)
    if friends_dict and FRIENDS_OF_FRIENDS:
        color_map = []
        for x in G.nodes() :
            if x in resolved:
                color_map.append('green')
            else: color_map.append('red')
        nx.draw(G,node_color = color_map,with_labels = LABELS)
    else :
        nx.draw(G,with_labels = LABELS)
    plt.show()

def load_verts_retweets():
    with open('verts.json') as f:
        verts = json.load(f)
    return verts

def resolve_verts():
    vs = load_verts()
    dict_ ={}
    res = []
    try :
        with open('resolve.json',) as f:
            dict_ = json.load(f)
    except :
        pass
    print (dict_)

    for v in vs :
        try :    
            x   = dict_.get(v[0]) or make_call(API.get_user,v[0])['screen_name']
            y   = dict_.get(v[1]) or make_call(API.get_user,v[1])['screen_name']
        
            dict_[v[0]] = x
            dict_[v[1]] = y

            print (v[0],x)
            print (v[1],y)
            res.append([x,y])
            with open('resolve.json','w') as f:
                json.dump(dict_,f)
        except:
            pass
    with open('verts.json','w') as f:
            json.dump(res,f)

def main():

    if (sys.argv[1] == 'resolve'):
        resolve_verts()

    if LOAD_VERTS :
        x = load_verts()
        graph_retweets([],[],[],x)
    else :
        if NO_COL :
            followers_ = followers({})
            x = build_tree_tweets(None,None,followers_)
        elif not USE_FILE :
            x = None
            if LOAD_PREVIOUS :
                try :
                    with open('rtws.json') as f:
                        x = json.load(f)
                    x = x['tweets_users'],x['retweets_users']
                except :
                    x = retweets(TAG)
            else :
                x = retweets(TAG)
            ids = ids_rt(x)
            followers_ = followers(ids)
            x = build_tree_tweets(x[0],x[1],followers_)
            with open('verts.json','w') as f:
                json.dump(list(x),f)
        else :
            x = load_verts()
        graph_retweets(*x)

if __name__ == '__main__':
    main()
