import json
import streamlit as st
import pymongo
import pandas as pd
from pymongo import MongoClient
import plotly
import plotly.express as px

st.set_page_config(
    page_title="Rap Français ",
    layout="wide"
)

st.title("Analyse des rappeurs français :")

st.write("Cette application, vise à avoir une vue globale de l'écosystème des rappeurs français.")
st.write("Premièrement, au niveau du nombre de morceaux et d'albums, mais ensuite en ce qui concerne leurs collaborations.")
st.write("Enfin, nous analyserons les lyrics.")
st.write("Même si la majorité des rappeurs français, sont présents dans cette base de donnée; certains sont manquants.")
st.write("De même, il manque les données de certains morceaux. En ce qui concerne les lyrics, l'analyse se fait sur un "
         "echantillon plus faible.")

st.write("----------")

st.subheader(" Première partie : analyse des différents résaux exsitants")

st.sidebar.subheader("Plus d'informations sur l'app :")

######## loading the data with func

# loading the json from pymongo

cluster = MongoClient(st.secrets["uri"], tls=True, tlsAllowInvalidCertificates=True)

db = cluster[st.secrets['db_name']]

collection = db['artist']

@st.cache
def get_all_artist():

    all_artist = list(db.artist_all_details.find())

    return all_artist


@st.cache
def query_a_single_rapper(rapper_name):

    return dict(db.artist_all_details.find_one({"name": rapper_name}))


@st.cache
def load_network_indiv():

    return pd.read_csv(".data/network_indiv_metrics.csv", sep=',', encoding='utf8')


@st.cache
def rapper_in_lyrics():

    rappeur_in_lyrics = list(db.lyrics.find({}, {"rappeur": 1, "_id": 0}))
    rappeur_lyrics_select = [artist['rappeur'] for artist in rappeur_in_lyrics]

    return rappeur_lyrics_select


# on rajoute le texte dans la sidebar
st.sidebar.write("----------")

st.sidebar.write("Voici quelques explications sur le fonctionnement de l'app et des lyrics.")

st.sidebar.write("Vous pouvez fermer cet onglet pour afficher le reste en plus grand.")

st.sidebar.write("----------")

st.sidebar.write("Voici la signification de certaines, des statistiques les plus importantes, pour mesurer un réseau : ")

st.sidebar.write("•	Clustering : Le coefficient de regroupement est une mesure de transitivité. "
                 "Plus précisément, le coefficient de regroupement d'un nœud est le rapport des liens existants "
                 "reliant les voisins d'un nœud au nombre maximal possible de tels liens.")

st.sidebar.write("•	Eccentricity : L’excentricité d’un sommet correspond au nombre de liens nécessaires pour relier "
                 "le sommet le plus distant. Plus l’excentricité est importante, moins le nœud est central.")

st.sidebar.write("•	Betweenness centrality : La centralité d’intermédiarité correspond au nombre de plus courts "
                 "chemins du graphe passant par chaque sommet.")

st.sidebar.write("----------")

st.sidebar.write("En ce qui concerne l'analyse des lyrics, elle a été réalisé avec nltk et avec Spacy. ")

st.sidebar.write("Le nombre de mots unique, correspond on différents mots uniques employés par le rappeur."
                 " Les mots non commun, correspondent aux mots qui ne font pas parties mots les plus utilisés "
                 "dans la langue française (il s'agit"
                 " souvent de déterminants ...), cette liste provient de spacy.")

# on retourne sur le fonctionnement de l'app
result = get_all_artist()

max_albums = list(db.artist_all_details.find({"nombre_albums": {"$gte": 5}}).sort("nombre_albums", -1))

st.write("le rappeur avec le plus d'albums est : ", max_albums[0]['name'], "avec un total de ", max_albums[0]['nombre_albums'])
st.write("le deuxième rappeur avec le plus d'albums est : ", max_albums[1]['name'], "avec un total de ",
         max_albums[1]['nombre_albums'])
st.write("le troisième rappeur avec le plus d'albums est : ", max_albums[2]['name'], "avec un total de ",
         max_albums[2]['nombre_albums'])

st.write("Selectionnez un rappeur dans la liste déroulante suivante (vous pouvez taper "
         "son nom plutot que de scroller indéfiniment) :")

# au préalable il faut faire une liste de tous les rappeurs dans la db
rappeur_liste = [i['name'] for i in result]
selected_rapper = st.selectbox('rappeur sélectionné :', options=rappeur_liste, key='rappeur_1')

# on affiche les stats du rappeur sélectionné:
query_rappeur_stats = query_a_single_rapper(selected_rapper)

# on fait 2 colonnes pour pas que ce ne soit ignoble
rap_c1, rap_c2 = st.columns(2)

with rap_c1:
    st.write("Nombre d'albums :", query_rappeur_stats['nombre_albums'])
    st.write("Nombre de morceaux :", len(query_rappeur_stats['all_unique_song']))
    try:
        st.write("Beatmaker favoris : ", max(query_rappeur_stats['beatmakers_repartition'],
                                            key=query_rappeur_stats['beatmakers_repartition'].get))
        st.write("Nombre de titres avec le beatmaker favori : ",
                 max(query_rappeur_stats['beatmakers_repartition'].values()))

    except ValueError:
        st.write("Pas de données sur les beatmakers pour ce rappeur")


with rap_c2:
    st.write("Ration de featuring :", round(query_rappeur_stats['ratio_featuring'], 3))
    try:
        st.write("Featuring favoris : ", max(query_rappeur_stats['featuring_repartition'],
                                             key=query_rappeur_stats['featuring_repartition'].get))
        st.write("Nombre de featuring, avec l'artist le plus featé :",
                 max(query_rappeur_stats['featuring_repartition'].values()))

    except ValueError:
        st.write("Cet artiste n'a réalisé aucun featuring, parmis les données que nous avons")


st.write("----------")

st.subheader(" Deuxième Partie : Analyse du Réseau des rappeurs : ")

st.write("Voici une première représentation du réseau de rappeur : "
         "Il existe une relation entre un des deux rappeurs lorsque l'un a feat avec l'autre et inversement."
         "Il n'y a pas de lien quand, les deux étaient en feats sur un même morceau ni quand il s'agit de membre "
         "d'un même groupe.")

st.write("La couleur représente le nombre de connexions à des rappeurs différents d'un rappeur : plus le point est"
         "clair, plus un rappeur a de connexions.")

st.write("Cette représentation du réseau, a été effectué avec l'algorithme Force Atlas 2.")
st.write("Le graph (comme les prochains) est inétractif ! Vous pouvez zoomer à l'intérieur et vous déplacer "
         "comme vous le souhaitez.")

fig = plotly.io.read_json(".data/network_atlas_version_finale.json")

st.plotly_chart(fig, use_container_width=True)

st.write("Contrairement à ce que l'on aurait pu imaginer, on ne distingue pas énormément de clusters ni de "
         "formes parituclières du réseau. Ce qui signifie que globalement les rappeurs collaborent beaucoup"
         "entres eux et qu'il ne le font pas uniquement avec leurs équipes."
         " Cela aurait pu être conterdit (ou non) si nous avions des liens qui prennent en compte le nombre de "
         "collaborations entre rappeurs (par exemple des traits plus ou moins marqués en fonction du nombre de "
         "collaborations).")

with open(".data/overall_metrics.json", encoding='utf-8') as fh:
    infos = json.load(fh)

st.write("voici quelques statistiques sur ce réseau :")

st.write("Il y a un total de ", infos['number_of_nodes'], " rappeurs dans ce réseaux.")
st.write("Pour un total de ", infos['number_of_edges'], " liens entres eux.")
st.write("Ce qui équivaut à une moyenne de ", round(infos['average_degree'], 3), " relations par rappeur.")
st.write("Le diamètre, c'est à dire la distance maximale entre deux rappeurs est de ", infos['diameter'], " !")
st.write("Le barycentre du réseau est : ", infos['barycenter'][0], " , en moyenne les rappeurs sont distants de lui de:",
         round(infos['average_distance_to_barycenter'], 3))
st.write("Le chemin moyen le plus court est de : ", round(infos['average_shortest_path'], 3), " ce qui sigifie "
                                                                                              "qu'en moyenne il faut "
                                                                                              "parcourir une "
                                                                                              "distance de ",
         round(infos['average_shortest_path'], 3), " pour relier deux rappeurs au hasard dans le réseau.")


# on load le df que maintenant
df = load_network_indiv()

# on load la distance du barycentre
with open(".data/distance_barycenter.json", encoding='utf-8') as fh:
    dist_bary = json.load(fh)

# on fait une liste des rappeurs présents pour
rapper_in_the_network = list(set(df['node']))

st.write("Cliquez ci-dessous pour afficher quelques graphiques sur le réseau :")

with st.expander("Cliquez ici pour afficher les différents graphiques : "):

    st.write("Voici quelques stats concernant les individus du réseau :")

    st.write("Voici les rappeurs avec le plus de degrés :")

    degree_df = df.sort_values(by=['degree'], ascending=False).head(30)
    degree_rank = px.bar(degree_df, x='degree', y='node', orientation='h')

    st.plotly_chart(degree_rank, use_container_width=True)

    st.write("Voici les rappeurs avec le plus haut niveau de clustering :")
    clustering_df = df.sort_values(by=['clustering'], ascending=False).head(30)
    clustering_rank = px.bar(clustering_df, x='clustering', y='node', orientation='h')

    st.plotly_chart(clustering_rank, use_container_width=True)

    st.write("Voici les rappeurs avec le plus de triangles:")
    triangles_df = df.sort_values(by=['triangles'], ascending=False).head(30)
    triangles_rank = px.bar(triangles_df, x='triangles', y='node', orientation='h')

    st.plotly_chart(triangles_rank, use_container_width=True)

    st.write("Vous pouvez décrouvrir les autres statistiques ci-desous : "
             "En cliquant sur une colonne vous triez par la valeur de celle-ci")

    st.write(df)

st.write("Cliquez ci-dessous pour afficher quelques statistiques sur n'importe quel rappeur:")

with st.expander("Cliquez ici pour afficher les stats pour chaque rappeur : "):

    st.write("Choisissez un rappeur dans la liste déroulante pour affciher ces stats parmis le réseau : ")

    network_rapper = st.selectbox("choisissez un rappeur :", options=rapper_in_the_network, key="rapper_network")

    data = df.copy()
    unique_rapper = data.loc[data['node'] == network_rapper]

    # on fait 2 colonnes pour que ce soit moins ignoble visuellement :
    c1, c2 = st.columns(2)

    with c1:

        st.write("Clustering :", unique_rapper['clustering'].iloc[0])
        st.write("Nombre de triangles :", unique_rapper['triangles'].iloc[0])
        st.write("Score Page Rank : ", unique_rapper['page_rank'].iloc[0])
        st.write('Eccentricity :', unique_rapper['eccentricity'].iloc[0])
        st.write("Distance du barycentre ", dist_bary[network_rapper])

    with c2:

        st.write("Nombre de liens  :", unique_rapper['degree'].iloc[0])
        st.write("Betweeness :", unique_rapper['betweeness'].iloc[0])
        st.write("closeness: ", unique_rapper['closeness'].iloc[0])
        st.write("Eigen Centrality ", unique_rapper['eigen_centrality'].iloc[0])
        st.write("Nombre de cliques : ", unique_rapper['clique'].iloc[0])

st.write("----------")

st.subheader(" Troisième partie : analyse du vocabulaire utilisé")

st.write("Tous les rappeurs ne sont pas présent (en tout cas pour le moment) dedans"
         "Il s'agit uniquement d'un petit echantillon")

st.write("Choisissez un rappeur pour découvrir les mots qu'ils utilisent le plus et dans quel mesure ils sont unqiue :")

rapper_lyrics_selection = rapper_in_lyrics()

lyrics_rapper_selected = st.selectbox('rappeur sélectionné :', options=rapper_lyrics_selection, key='rappeur_lyrics')

# on affiche les stats du rappeur en question

# on fait une query où l'on ne retourne pas tout
query_lyrics_rapper = list(db.lyrics.find({"rappeur": lyrics_rapper_selected}, {"_id": 0, "nombre_titres": 1,
                                                                           "nombre_mots_par_titre": 1,
                                                                           "ratio_unique": 1,
                                                                           "avg_non_commun_tire": 1}))
c1_lyrics, c2_lyrics = st.columns(2)

with c1_lyrics:

    st.write("Nombre  de titres", query_lyrics_rapper[0]['nombre_titres'])
    st.write("Nombre  de mots par titre", query_lyrics_rapper[0]['nombre_mots_par_titre'])

with c2_lyrics:

    st.write("Ratio de mot unique", query_lyrics_rapper[0]['ratio_unique'])
    st.write("Nombre moyen de mots non communs par titre", query_lyrics_rapper[0]['avg_non_commun_tire'])

st.write('------------')

st.write("Voici deux scatter plots permettant de représenter les différences en termes de myrics entre ces différents"
         "rappeurs.")

query_rapper_graph = list(db.lyrics.find({}, {"_id": 0, "rappeur": 1, "nombre_mots_par_titre": 1,
                                              "ratio_unique": 1, "avg_non_commun_tire": 1}))

dff = pd.DataFrame(query_rapper_graph)

st.write("Le graphique suivant représente, le nombre  de mots moyen par titre et le nombre de mots non communs"
         " par titre.")

almost_last_fig = px.scatter(data_frame=dff, x='nombre_mots_par_titre', y='avg_non_commun_tire', hover_name="rappeur")

st.plotly_chart(almost_last_fig, use_container_width=True)

last_fig = px.scatter(data_frame=dff, x='nombre_mots_par_titre', y='ratio_unique', hover_name="rappeur")

st.write("Le graphique suivant représente, le nombre  de mots moyen par titre et le nombre de différents"
         " moyens par titre.")

st.plotly_chart(last_fig, use_container_width=True)

st.write("---------")

st.write("Tapez ci-dessous un mot pour connaitre son occurence, parmi les lyrics de tous les rappeurs "
         "attention les majuscules et accents sont importants.")

word_query_param = st.text_input("Ecrivez un mot pour connaitre son occurence totale. Il faut appuyer sur Entrée pour"
                                 " effectuer la requete.", "Marseille")

word_query = db.global_lyrics_v2.find_one({"word": word_query_param})


if word_query is not None:
    st.write("Le mot ", word_query_param, " apparait un total de ", word_query['count'], " fois, dans notre "
                                                                                         "echantilllon de lyrics")
else:
    st.write("Le mot ", word_query_param, " n' apparait pas dans nos lyrics. Vous pouvez essayer de changer les "
                                          "majusucules ou les accents, si vous pensez qu'il devrait être présent")
