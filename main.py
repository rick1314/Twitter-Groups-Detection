import tweepy
from time import sleep
import json
import networkx as nx
import matplotlib.pyplot as plt

#This the time to wait for the rate limit to be cleared
SLEEP_TIME          = 60*15
#The name of the file containing the nodes, must be within the same directory
FILE_NAME           = 'nodes.txt'

#You need to create an app to get ACCESS_TOKEN, and ACCESS_SECRET
CONSUMER_KEY        = '69ggjTQyouix1NngdXw6sNZhm'
CONSUMER_SECRET     = '3gSSUwkkPpdD2G0PJrM65l8FXUDZ4VNzvU9GIIyVFRfKxTySWt'
ACCESS_TOKEN        = '564947083-QvqH3twoAl2ha66fkNL2yI11zkI9efiPdBs0fP31'
ACCESS_SECRET       = 'dj21xXjX9vQC7UowCZEutSRghCyOF4b3o7vvcTV9LqTr2'

#If set to true, the graph will contain an shared friends between nodes, keep in mind
#that this will increase the number of edges in very very large way
FRIENDS_OF_FRIENDS  = False
#consider the list of people follwoing the node
FOLLOWING           = True
#Consider the list of people followed by the node
FOLLOWED            = True
#Use the last generated vertices file
USE_FILE            = True
#Display labels
LABELS              = True

#Dsiplays isolated nodes
ISOLATED            = True

def auth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth)

API = auth()

def load():
    with open(FILE_NAME) as f :
        res = reversed([x.strip() for x in f.readlines() if x.strip()!=''])
    return res

def make_call(func,*args):
    while True :
        try :
            return func(*args)
        except Exception as e :
            print (e)
            print ('Sleeping for {} seconds'.format(SLEEP_TIME))
            sleep(SLEEP_TIME)

def resolve(names,api=API):
    res = {}
    for name in names :
        res[name] = make_call(api.get_user,name).id
    return res

def followers(ids,api = API):
    ids =  [ids[x] for x in ids]
    res = {}
    for id in ids:
        res[id]     = {}

        if FOLLOWED :
            print ('Getting followers for : {}'.format(id))
            res[id]['followed'] =  make_call(api.followers_ids,id)

        if FOLLOWING :
            print ('Getting friends for : {}'.format(id))
            res[id]['following'] =  make_call(api.friends_ids,id)
    return res

def build_tree(friends_dict,resolved):
    verts = []
    for id in friends_dict :
        if FOLLOWED :
            for x in friends_dict[id]['followed']    :
                if check(id,x,friends_dict):
                    verts.append([int(id),x])
        if FOLLOWING :
            for y in friends_dict[id]['following']    :
                if check(id,y,friends_dict):
                    verts.append([int(id),y])
    inv_res = {resolved[x] : x for x in resolved}
    for x in verts :
        if inv_res.get(x[0],False):
            x[0] =  inv_res[x[0]]

        if inv_res.get(x[1],False):
            x[1] =  inv_res[x[1]]
    return verts

def save_verts(verts,name = 'verts.json'):
    with open(name,'w') as f:
        json.dump(verts,f)

def load_verts(name = 'verts.json'):
    with open(name) as f:
        verts = json.load(f)
    return verts

def check(id,x,friends_dict):
    for y in friends_dict :
        y = int(y)
        id = int(id)
        if y!= id :
            if not FRIENDS_OF_FRIENDS :
                if x == y :
                    return True
            elif x == y or (FOLLOWED and x in friends_dict[y]['followed']) or ( FOLLOWING and x in friends_dict[y]['following'] ) :
                return True
    return False

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
        plt.savefig('graph.png', dpi=100)
        plt.show()
		
def main():
    _dict = None
    if not USE_FILE :
        nodes = load()
        resolved = resolve(nodes)
        _dict = followers(resolved)
        save_verts(_dict,name='dict.json')
        save_verts(resolved,name='res.json')

    resolved = load_verts(name='res.json')
    _dict = load_verts(name='dict.json')
    verts = build_tree(_dict,resolved)
    save_verts(verts)
    verts = load_verts()
    graph(verts,resolved,_dict)



if __name__ == '__main__':
    main()
