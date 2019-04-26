from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.conf import settings
from graph_app.models import GraphItem, SongsItems

# External APP libraries
import logging
import json
import os
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
from networkx.algorithms.community import greedy_modularity_communities
import pandas as pd


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')


def index(request):
    """ Entry point for the Graph web app
    @input: request: Request object from user

    @output: render object
    """
    G = generate_graph()
    graph_density = nx.density(G)
    connected = nx.is_connected(G)
    try:
        graph_diameter = nx.diameter(G)
    except Exception as e:
        logging.info(f'Graph is not connected calculating subgraphs')
        largest_subgraph = max(nx.connected_component_subgraphs(G), key=len)
        graph_diameter = nx.diameter(largest_subgraph)
        length_subg = len(largest_subgraph)
        logging.info(f'Obtained largest subgraph with length of {length_subg}')
    return render(request, 'index.html', context={"density": round(graph_density, 3), "diameter": graph_diameter, "is_connected": connected, "subgraph_length": length_subg})


def eigenvector_view(request):
    """ Endpoint to request eigenvector view
    @input: request: Request object from user

    @output: render object
    """
    return render(request, 'eigenvector_centrality.html')


def page_rank_view(request):
    """ Endpoint to request eigenvector view
    @input: request: Request object from user

    @output: render object
    """
    return render(request, 'page_rank.html')


def modularity_view(request):

    return render(request, 'modularity.html')

def get_main_graph(request):
    """ API Endpoint to get the initial graph JSON
    @input request: request object from user

    @output JsonResponse: json containing graph data
    """

    logging.info('Request received')
    G = generate_graph()
    data = generate_d3_format(G)

    return JsonResponse(data, safe=False)


def calculate_eigenvector(request):
    """ This endpoints calculates the eigenvector centrality for the graph object
    @input request: Request object from user.

    @output data: Json object with eigenvector data calculated
    """
    logging.info('Calculating eigenvector centrality')
    G = generate_graph()

    centrality = nx.eigenvector_centrality(G)
    node_names = list(centrality.keys())
    data = generate_d3_format(G)

    index = 0
    while index < len(data['nodes']):
        node = data['nodes'][index]
        if node['id'] in node_names:
            data['nodes'][index]['eigen_centrality'] = centrality[node['id']]

        index += 1

    return JsonResponse(data, safe=False)


def calculate_pagerank(request):
    logging.info('Calculating page rank centrality')
    G = generate_graph()

    page_rank = nx.pagerank_numpy(G, weight='weight')
    node_names = list(page_rank.keys())
    data = generate_d3_format(G)

    index = 0
    while index < len(data['nodes']):
        node = data['nodes'][index]
        if node['id'] in node_names:
            data['nodes'][index]['page_rank'] = page_rank[node['id']]

        index += 1

    return JsonResponse(data, safe=False)


def calculate_modularity(request):
    logging.info('Calculating modularity')

    G = generate_graph()
    data = generate_d3_format(G)

    modularity = list(greedy_modularity_communities(G))
    logging.info(len(modularity))
    index = 0
    while (index < len(modularity)):
        for cluster_node in modularity[index]:
            for position, node in enumerate(data['nodes']):
                if cluster_node == node['id']:
                    data['nodes'][position]['cluster'] = index
        
        index +=1

    return JsonResponse(data, safe=False)

####################################################### TOOL METHODS #######################################################
############################################################################################################################

def add_default_values_node(node):
    """ Function add default data to non well formatted nodes
    @input node: dict object containing node data

    @output node: dict object with default values on non existing keys
    """
    # Default values for the node if not exists
    keys = {'weight': 0, 'genre': 'Other'}
    for k in keys.keys():
        if k not in node:
            node[k] = keys[k]
    return node  


def load_data(request):
    """ This endpoint fills database with static JSON file with graph data
    @input: request: Request object from client.
    """

    graph_data = pd.read_json(os.path.join(settings.BASE_DIR, 'graph_app/static/Graph_data_link_weight.json'), orient='records')
    songs = pd.read_json(os.path.join(settings.BASE_DIR, 'graph_app/static/Graph_data.json'), orient='records')
    
    songs.apply(fill_songs_DB, axis=1)
    graph_data.apply(fill_graph_DB, axis=1)  
    
    logging.info(f'{graph_data.shape[0]} items loaded')
    return render(request, 'index.html')


def generate_graph():
    """ This function reads graph data from database and creates the graph object
    @output: G: Graph object from networkX
    """
    logging.info('Generating basic graph')

    graph_items = GraphItem.objects.all()
    G = nx.Graph()
    for item in graph_items:
        G.add_node(item.artist_name, weight=item.view_count, genre=item.genre)
        G.add_edges_from([(item.artist_name, item.feat_artist_name, {'weigth': item.num_feats})])

    logging.info('Graph generated successfully')

    return G


def generate_d3_format(G):
    data = json_graph.node_link_data(G)
    data['nodes'] = [add_default_values_node(node) for node in data['nodes']]

    return data


########################## INITIAL FUNCTIONS TO FILL THE GRAPH ############################
###########################################################################################

def fill_graph_DB(row):
    """ Function called by apply of dataframe to fill Graph database
    @input: row: dataframe row with graph data
    """
    new_db_item = GraphItem(
            artist_name=row['artist_name'],
            view_count=row['view_count'],
            feat_artist_name=row['feat_artist_name'],
            grade=row['grade'],
            sub_count=row['subs_count'],
            num_feats=row['num_feats'],
            genre=row['genre'],
            yt_channel_id=row['YT_channel_id'],
            yt_channel_name=row['YT_channel_name']
            )
    new_db_item.save()


def fill_songs_DB(row):
    """ Function called by apply of dataframe to fill Songs database
    @input: row: dataframe row with graph data
    """
    new_db_item = SongsItems(
        artist = row['artist_name'],
        feat_artist = row['feat_artist_name'],
        song = row['song']
    )
    new_db_item.save()