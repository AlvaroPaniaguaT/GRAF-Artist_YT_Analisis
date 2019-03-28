from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.conf import settings
from graph_app.models import GraphItem

# External APP deps
import logging
import json
import os
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph


G = nx.Graph()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')


"""
    Entry point for the Graph web app
"""
def index(request):
    return render(request, 'index.html')

"""
    API Endpoint to get the initial graph
"""
def get_main_graph(request):
    logging.info('Request received')
    graph_items = GraphItem.objects.all()

    for item in graph_items:
        G.add_node(item.artist_name, weight=item.view_count)
        G.add_edges_from([(item.artist_name, item.feat_artist_name, {'weigth': item.grade})])
    
    data = json_graph.node_link_data(G)
    logging.info(data['nodes'][0])
    logging.info(data['links'][0])
    return JsonResponse(data, safe=False)


def calculate_betweeness(request):
    pass


"""
    This endpoint fills database with static JSON file
    with graph data
"""
def load_data(request):
    f = open(os.path.join(settings.BASE_DIR, 'graph_app/static/Graph_data.json'))
    graph_content = json.loads(f.read())

    for item in graph_content:
        new_db_item = GraphItem(
            artist_name=item['artist_name'],
            view_count=item['view_count'],
            feat_artist_name=item['feat_artist_name'],
            grade=item['grade'],
            sub_count=item['subs_count'],
            genre=item['genre'],
            song=item['song'],
            yt_channel_id=item['YT_channel_id'],
            yt_channel_name=item['YT_channel_name']
            )
        new_db_item.save()
    
    logging.info(f'{len(graph_content)} items loaded')
    return render(request, 'index.html')