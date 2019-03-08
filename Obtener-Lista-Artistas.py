from lxml import html
import requests

req = requests.get('https://www.todomusica.org/listado-artistas.shtml')
tree = html.fromstring(req.content)

artist_list = tree.xpath('//div/div[2]/a')

artist_file = open('Lista_Artista.txt', 'w', encoding='utf-8')
print("Writing %s artists." % str(len(artist_list)))
for artist_name in artist_list:
    artist_file.write(artist_name.text)
    artist_file.write('\n')