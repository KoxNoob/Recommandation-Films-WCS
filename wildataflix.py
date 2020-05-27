# Import des librairies
import pandas as pd
import streamlit as st
import numpy as np
import time
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import plotly.graph_objects as go

read_and_cache_csv = st.cache(pd.read_csv)
display_min = 0
display_max = 5
sns.set()
st.sidebar.image(
    'https://github.com/KoxNoob/Recommandation-Films-WCS/blob/master/wildataflix.png?raw=true',
    width=300)

st.sidebar.title("Menu")
vue = st.sidebar.radio("", ('Accueil', 'Recommandations', 'Administrateur'))

if vue == 'Accueil':
    st.markdown(
        "<h3 style='text-align: center; color: black; size = 0'>Tu es à court d\'idée ? Tu ne sais plus quoi regarder ? Alors passe à la partie Recommandations, nous allons t\'aider !</h3>",
        unsafe_allow_html=True)
    st.image('https://github.com/KoxNoob/Recommandation-Films-WCS/blob/master/accueil_2.jpeg?raw=true', width=650)

if vue == 'Recommandations':
    st.markdown(
        "<h3 style='text-align: center; color: grey; size = 0'>Maintenant que tu es bien installé, il n'y a plus qu'à entrer tes préférences dans la barre de navigation à gauche, on s'occupe du reste !</h3>",
        unsafe_allow_html=True)
    attente = np.random.choice(['Tiens, et si tu allais te chercher une bière ? Ou du popcorn ? Non ? Tu as raison, \
                                tout est prêt, voici notre sélection ! ', \
                                'Il va falloir choisir Néo. La pilule bleue, ou la pilule rouge ?', 'Il s\'appelle Juste le Blanc. Son prénom c\'est \
                                Juste, et son nom c\'est le Blanc.',
                                'Que la force de la recommandation soit avec toi !', 'Non pas toi Obélix, tu \
                                es tombé dedans quand tu étais petit !', "Vers l'infini et au-delà", "La vie c’est \
                                comme une boîte de chocolats, on ne sait jamais sur quoi on va tomber.", \
                                "Partout où il y a grandeur, grandeur du souverain ou du pouvoir et même de la \
                                pensée et des passions, l'erreur elle aussi est grande.", "Monde de merde",
                                "Tu bluffes Martoni", "Tu vois, le monde se divise en deux catégories: ceux qui ont \
                                un pistolet chargé et ceux qui creusent. Toi tu creuses", "Écoute Bernard… J’crois que toi \
                                et moi, on a un peu le même problème ; c’est qu’on peut pas vraiment tout miser sur notre \
                                physique, surtout toi. Alors si je peux me permettre de te donner un conseil, c’est oublie qu’t’as \
                                aucune chance, vas-y, fonce ! On sait jamais, sur un malentendu ça peut marcher…" ,\
                                "Ou tu sors ou j'te sors mais faudra prendre une décision","Si je te dis que t'es tendue, c'est que \
                                 t'es tendue Natacha !", "Merci la gueuse. Tu es un laideron mais tu es bien bonne.", "J'aime me beurrer \
                                la biscotte"])



    @st.cache(persist=True)
    def csv(path):
        df_movies = pd.read_csv(path)
        df_movies.drop(['Unnamed: 0'], axis=1, inplace=True)
        return df_movies


    df_movies = csv('https://raw.githubusercontent.com/KoxNoob/Recommandation-Films-WCS/master/df_movies.csv')

    ###### Définition des fonctions ######

    sex = st.sidebar.selectbox('Ton sexe ?',
                               ('Femme', 'Homme', 'Peu importe'), 2)

    age = st.sidebar.selectbox('Dans quelle tranche d\'âge tu te situes ?',
                               ('18-29 ans', '30-44 ans', '+ de 45 ans'), 2)

    genre = st.sidebar.selectbox('Quel genre de films aimes-tu ?',
                                 ('Biography', 'Drama', 'Adventure', 'History', 'Crime', 'Western', 'Fantasy', 'Comedy',
                                  'Horror', 'Family', 'Action' \
                                      , 'Romance', 'Mystery', 'Animation', 'Sci-Fi', 'Musical', 'Thriller', 'Music',
                                  'Film-Noir', 'War', 'Sport', 'Adult' \
                                      , 'Documentary'), 12)

    note = st.sidebar.slider('Quelle est la note moyenne des films que tu aimerais voir ?', 0, 10, 7)

    values = st.sidebar.slider('Sélectionne un intervalle d\'années de sortie de films', 1906, 2019, (1990, 2010))
    annee_min = values[0]
    annee_max = values[1]


    @st.cache
    # Séparation du df en fonction du sexe
    def df_sexe(sex, df):
        if sex == 'Femme':
            df_female = df_movies[['imdb_title_id', 'title', 'year', 'genre 1', 'duration',
                                   'average_votes', 'females_18age_avg_vote',
                                   'females_30age_avg_vote', 'females_45age_avg_vote', 'director',
                                   'actor_1', 'actor_2', 'description', 'g_Action', 'g_Adult',
                                   'g_Adventure', 'g_Animation', 'g_Biography', 'g_Comedy', 'g_Crime',
                                   'g_Documentary', 'g_Drama', 'g_Family', 'g_Fantasy', 'g_Film-Noir',
                                   'g_History', 'g_Horror', 'g_Music', 'g_Musical', 'g_Mystery',
                                   'g_Romance', 'g_Sci-Fi', 'g_Sport', 'g_Thriller', 'g_War', 'g_Western']]
            return df_female
        elif sex == 'Homme':
            df_male = df_movies[['imdb_title_id', 'title', 'year', 'genre 1', 'duration',
                                 'average_votes', 'males_18age_avg_vote',
                                 'males_30age_avg_vote', 'males_45age_avg_vote', 'director',
                                 'actor_1', 'actor_2', 'description', 'g_Action', 'g_Adult',
                                 'g_Adventure', 'g_Animation', 'g_Biography', 'g_Comedy', 'g_Crime',
                                 'g_Documentary', 'g_Drama', 'g_Family', 'g_Fantasy', 'g_Film-Noir',
                                 'g_History', 'g_Horror', 'g_Music', 'g_Musical', 'g_Mystery',
                                 'g_Romance', 'g_Sci-Fi', 'g_Sport', 'g_Thriller', 'g_War', 'g_Western']]
            return df_male
        else:
            df_all = df_movies[['imdb_title_id', 'title', 'year', 'genre 1', 'duration',
                                'average_votes', 'allgenders_18age_avg_vote',
                                'allgenders_30age_avg_vote', 'allgenders_45age_avg_vote',
                                'director', 'actor_1', 'actor_2', 'description', 'g_Action', 'g_Adult',
                                'g_Adventure', 'g_Animation', 'g_Biography', 'g_Comedy', 'g_Crime',
                                'g_Documentary', 'g_Drama', 'g_Family', 'g_Fantasy', 'g_Film-Noir',
                                'g_History', 'g_Horror', 'g_Music', 'g_Musical', 'g_Mystery',
                                'g_Romance', 'g_Sci-Fi', 'g_Sport', 'g_Thriller', 'g_War', 'g_Western']]
            return df_all


    df_user = df_sexe(sex, df_movies)


    @st.cache(allow_output_mutation=True)
    def recommandation(sex, age, genre, note):
        global reco
        Mask = pd.DataFrame()
        my_columns = []
        Top5 = pd.DataFrame()
        samples = pd.DataFrame()
        if genre == 'Biography':
            Mask = pd.DataFrame({'g_Biography': [1]})
            my_columns = ['imdb_title_id', 'g_Biography']

        if genre == 'Drama':
            Mask = pd.DataFrame({'g_Drama': [1]})
            my_columns = ['imdb_title_id', 'g_Drama']

        if genre == 'Adventure':
            Mask = pd.DataFrame({'g_Adventure': [1]})
            my_columns = ['imdb_title_id', 'g_Adventure']

        if genre == 'History':
            Mask = pd.DataFrame({'g_History': [1]})
            my_columns = ['imdb_title_id', 'g_History']

        if genre == 'Crime':
            Mask = pd.DataFrame({'g_Crime': [1]})
            my_columns = ['imdb_title_id', 'g_Crime']

        if genre == 'Western':
            Mask = pd.DataFrame({'g_Western': [1]})
            my_columns = ['imdb_title_id', 'g_Western']

        if genre == 'Fantasy':
            Mask = pd.DataFrame({'g_Fantasy': [1]})
            my_columns = ['imdb_title_id', 'g_Fantasy']

        if genre == 'Comedy':
            Mask = pd.DataFrame({'g_Comedy': [1]})
            my_columns = ['imdb_title_id', 'g_Comedy']

        if genre == 'Horror':
            Mask = pd.DataFrame({'g_Horror': [1]})
            my_columns = ['imdb_title_id', 'g_Horror']

        if genre == 'Family':
            Mask = pd.DataFrame({'g_Family': [1]})
            my_columns = ['imdb_title_id', 'g_Family']

        if genre == 'Action':
            Mask = pd.DataFrame({'g_Action': [1]})
            my_columns = ['imdb_title_id', 'g_Action']

        if genre == 'Romance':
            Mask = pd.DataFrame({'g_Romance': [1]})
            my_columns = ['imdb_title_id', 'g_Romance']

        if genre == 'Mystery':
            Mask = pd.DataFrame({'g_Mystery': [1]})
            my_columns = ['imdb_title_id', 'g_Mystery']

        if genre == 'Animation':
            Mask = pd.DataFrame({'g_Animation': [1]})
            my_columns = ['imdb_title_id', 'g_Animation']

        if genre == 'Sci-Fi':
            Mask = pd.DataFrame({'g_Sci-Fi': [1]})
            my_columns = ['imdb_title_id', 'g_Sci-Fi']

        if genre == 'Musical':
            Mask = pd.DataFrame({'g_Musical': [1]})
            my_columns = ['imdb_title_id', 'g_Musical']

        if genre == 'Thriller':
            Mask = pd.DataFrame({'g_Thriller': [1]})
            my_columns = ['imdb_title_id', 'g_Thriller']

        if genre == 'Music':
            Mask = pd.DataFrame({'g_Music': [1]})
            my_columns = ['imdb_title_id', 'g_Music']

        if genre == 'Film-Noir':
            Mask = pd.DataFrame({'g_Film-Noir': [1]})
            my_columns = ['imdb_title_id', 'g_Film-Noir']

        if genre == 'War':
            Mask = pd.DataFrame({'g_War': [1]})
            my_columns = ['imdb_title_id', 'g_War']

        if genre == 'Sport':
            Mask = pd.DataFrame({'g_Sport': [1]})
            my_columns = ['imdb_title_id', 'g_Sport']

        if genre == 'Adult':
            Mask = pd.DataFrame({'g_Adult': [1]})
            my_columns = ['imdb_title_id', 'g_Adult']

        if genre == 'Documentary':
            Mask = pd.DataFrame({'g_Documentary': [1]})
            my_columns = ['imdb_title_id', 'g_Documentary']

        if sex == 'Femme':
            if age == '18-29 ans':
                Mask.insert(1, 'females_18age_avg_vote', note)
                my_columns.append('females_18age_avg_vote')
            if age == '30-44 ans':
                Mask.insert(1, 'females_30age_avg_vote', note)
                my_columns.append('females_30age_avg_vote')
            if age == '+ de 45 ans':
                Mask.insert(1, 'females_45age_avg_vote', note)
                my_columns.append('females_45age_avg_vote')
            samples = df_user[my_columns]
            dataflix = NearestNeighbors(n_neighbors=50)
            dataflix.fit(samples.iloc[:, 1:])
            temp = pd.DataFrame()
            for i in range(50):
                indice_recommandation = dataflix.kneighbors(Mask)[1][0][i]
                picsou = samples.iloc[indice_recommandation, :][0]
                Top5 = pd.concat([temp, df_user[df_user['imdb_title_id'] == picsou]])
                temp = Top5
            if age == '18-29 ans':
                Top5 = Top5.sort_values(by='females_18age_avg_vote', ascending=False)
                Top5 = Top5[Top5['year'].between(annee_min, annee_max)]
            if age == '30-44 ans':
                Top5 = Top5.sort_values(by='females_30age_avg_vote', ascending=False)
                Top5 = Top5[Top5['year'].between(annee_min, annee_max)]
            if age == '+ de 45 ans':
                Top5 = Top5.sort_values(by='females_45age_avg_vote', ascending=False)
                Top5 = Top5[Top5['year'].between(annee_min, annee_max)]

        if sex == 'Homme':
            if age == '18-29 ans':
                Mask.insert(1, 'males_18age_avg_vote', note)
                my_columns.append('males_18age_avg_vote')
            if age == '30-44 ans':
                Mask.insert(1, 'males_30age_avg_vote', note)
                my_columns.append('males_30age_avg_vote')
            if age == '+ de 45 ans':
                Mask.insert(1, 'males_45age_avg_vote', note)
                my_columns.append('males_45age_avg_vote')
            samples = df_user[my_columns]
            dataflix = NearestNeighbors(n_neighbors=50)
            dataflix.fit(samples.iloc[:, 1:])
            temp = pd.DataFrame()
            for i in range(50):
                indice_recommandation = dataflix.kneighbors(Mask)[1][0][i]
                picsou = samples.iloc[indice_recommandation, :][0]
                Top5 = pd.concat([temp, df_user[df_user['imdb_title_id'] == picsou]])
                temp = Top5
            if age == '18-29 ans':
                Top5 = Top5.sort_values(by='males_18age_avg_vote', ascending=False)
                Top5 = Top5[Top5['year'].between(annee_min, annee_max)]
            if age == '30-44 ans':
                Top5 = Top5.sort_values(by='males_30age_avg_vote', ascending=False)
                Top5 = Top5[Top5['year'].between(annee_min, annee_max)]
            if age == '+ de 45 ans':
                Top5 = Top5.sort_values(by='males_45age_avg_vote', ascending=False)
                Top5 = Top5[Top5['year'].between(annee_min, annee_max)]

        if sex == 'Peu importe':
            if age == '18-29 ans':
                Mask.insert(1, 'allgenders_18age_avg_vote', note)
                my_columns.append('allgenders_18age_avg_vote')
            if age == '30-44 ans':
                Mask.insert(1, 'allgenders_30age_avg_vote', note)
                my_columns.append('allgenders_30age_avg_vote')
            if age == '+ de 45 ans':
                Mask.insert(1, 'allgenders_45age_avg_vote', note)
                my_columns.append('allgenders_45age_avg_vote')
            samples = df_user[my_columns]
            dataflix = NearestNeighbors(n_neighbors=50)
            dataflix.fit(samples.iloc[:, 1:])
            temp = pd.DataFrame()
            for i in range(50):
                indice_recommandation = dataflix.kneighbors(Mask)[1][0][i]
                picsou = samples.iloc[indice_recommandation, :][0]
                Top5 = pd.concat([temp, df_user[df_user['imdb_title_id'] == picsou]])
                temp = Top5
            if age == '18-29 ans':
                Top5 = Top5.sort_values(by='allgenders_18age_avg_vote', ascending=False)
                Top5 = Top5[Top5['year'].between(annee_min, annee_max)]
            if age == '30-44 ans':
                Top5 = Top5.sort_values(by='allgenders_30age_avg_vote', ascending=False)
                Top5 = Top5[Top5['year'].between(annee_min, annee_max)]
            if age == '+ de 45 ans':
                Top5 = Top5.sort_values(by='allgenders_45age_avg_vote', ascending=False)
                Top5 = Top5[Top5['year'].between(annee_min, annee_max)]
        return Top5


    @st.cache(persist=True)
    def api_request(snip):
        url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/" + snip
        headers = {
            'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com",
            'x-rapidapi-key': "deaf55a4eemsh7c2792b225d2a3cp123471jsn98f0d82fd8f8"
        }
        response = requests.request("GET", url, headers=headers)
        return (response.text)


    @st.cache(persist=True)
    def token(string):
        start = 0
        i = 0
        token_list = []
        for x in range(0, len(string)):
            if '"' == string[i:i + 1][0]:
                token_list.append(string[start:i + 1])
                start = i + 1
            i += 1
        token_list.append(string[start:i + 1])
        return token_list[27]


    @st.cache(persist=True)
    def cleaner(parsed):
        parsed = parsed.replace('poster', '')
        parsed = parsed.replace('"', '')
        parsed = parsed.replace(',', '')
        parsed = parsed.replace('\\', '')
        parsed = parsed.lstrip(':')
        return parsed


    @st.cache(persist=True)
    def list_parser(liste):
        url_list = []
        for i in range(len(liste)):
            raw = api_request(liste[i])
            parsed = token(raw)
            clean_url = cleaner(parsed)
            url_list.append(clean_url)
        for x in range(1, len(url_list) + 1):
            if url_list[x - 1] == "":
                url_list[x - 1] = "https://github.com/KoxNoob/Recommandation-Films-WCS/blob/master/image.png?raw=true"

        return url_list

    lenght = True
    reco = recommandation(sex, age, genre, note)
    reco.rename(columns={'title': 'Titre', 'year': 'Année', 'director': 'Réalisateur', 'average_votes': 'Note',
                         'genre 1': 'Genre', 'duration': 'Durée'}, inplace=True)
    reco['Note'] = reco['Note'].apply(lambda x: round(x))
    parsed_list = list_parser(
        list(reco['imdb_title_id'].unique()))
    if st.sidebar.button('Afficher les films du Top 6 à 10'):
        display_min += 5
        display_max += 5
    if len(parsed_list) >= display_max:
        lenght = True
    else :
        lenght = False

    with st.spinner(attente):
        time.sleep(5)
    if lenght:

        st.success('Tadam !')


        reco = reco.drop(['imdb_title_id'], axis=1).reset_index(drop=True)
        reco.index = reco.index + 1

        st.image([parsed_list[display_min],parsed_list[display_min+1],parsed_list[display_min+2],parsed_list[display_min+3],parsed_list[display_min+4]], width=126)
        fig = go.Figure(data=[go.Table(columnorder=[1, 2, 3, 4, 5, 6],
                                       columnwidth=[10, 50, 15, 20, 10, 10],
                                       header=dict(values=['N°', 'Titre', 'Année', 'Genre', 'Note', "Durée"],
                                                   fill_color='red', line=dict(width=2),
                                                   font=dict(color='white', size=14)),
                                       cells=dict(values=[reco.index.values[display_min:display_max],
                                                          reco.Titre.values[display_min:display_max], \
                                                          reco.Année.values[display_min:display_max],
                                                          reco.Genre.values[display_min:display_max], \
                                                          reco.Note.values[display_min:display_max],
                                                          reco.Durée.values[display_min:display_max]],
                                                  fill_color=['red', 'black'], font=dict(color='white', size=[14, 12]),
                                                  line=dict(width=2), height=30))])
        fig.update_layout(width=1200, height=200, margin=dict(l=20, r=20, t=0, b=0, pad=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<h1 style='text-align: center; color: black; size = 0'>Fiches descriptives</h1>",
                    unsafe_allow_html=True)
        # CI film n°1
        st.markdown("----------------------------------------------------------")
        st.markdown(
            "<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 0, 0]) + " (" + \
            str(reco.iloc[display_min + 0, 1]) + ")" "</h2>", unsafe_allow_html=True)
        st.markdown('<p align="center"><img width="150" height="220" src=' + parsed_list[0] + "</p>", unsafe_allow_html=True)
        st.write('Réalisateur : ' + str(reco.iloc[display_min + 0, 8]))
        st.write(
            'Acteurs principaux : ' + str(reco.iloc[display_min + 0, 9]) + ', ' + str(reco.iloc[display_min + 0, 10]))
        st.write('Synopsis : ' + str(reco.iloc[display_min + 0, 11]))
        st.markdown("----------------------------------------------------------")
        # CI film n°2
        st.markdown(
            "<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 1, 0]) + " (" + \
            str(reco.iloc[display_min + 1, 1]) + ")" "</h2>", unsafe_allow_html=True)
        st.markdown('<p align="center"><img width="150" height="220" src=' + parsed_list[1] + "</p>", unsafe_allow_html=True)
        st.write('Réalisateur : ' + str(reco.iloc[display_min + 1, 8]))
        st.write(
            'Acteurs principaux : ' + str(reco.iloc[display_min + 1, 9]) + ', ' + str(reco.iloc[display_min + 1, 10]))
        st.write('Synopsis : ' + str(reco.iloc[display_min + 1, 11]))
        st.markdown("----------------------------------------------------------")
        # CI film n°3
        st.markdown(
            "<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 2, 0]) + " (" + \
            str(reco.iloc[display_min + 2, 1]) + ")" "</h2>", unsafe_allow_html=True)
        st.markdown('<p align="center"><img width="150" height="220" src=' + parsed_list[2] + "</p>", unsafe_allow_html=True)
        st.write('Réalisateur : ' + str(reco.iloc[display_min + 2, 8]))
        st.write(
            'Acteurs principaux : ' + str(reco.iloc[display_min + 2, 9]) + ', ' + str(reco.iloc[display_min + 2, 10]))
        st.write('Synopsis : ' + str(reco.iloc[display_min + 2, 11]))
        st.markdown("----------------------------------------------------------")
        # CI film n°4
        st.markdown(
            "<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 3, 0]) + " (" + \
            str(reco.iloc[display_min + 3, 1]) + ")" "</h2>", unsafe_allow_html=True)
        st.markdown('<p align="center"><img width="150" height="220" src=' + parsed_list[3] + "</p>", unsafe_allow_html=True)
        st.write('Réalisateur : ' + str(reco.iloc[display_min + 3, 8]))
        st.write(
            'Acteurs principaux : ' + str(reco.iloc[display_min + 3, 9]) + ', ' + str(reco.iloc[display_min + 3, 10]))
        st.write('Synopsis : ' + str(reco.iloc[display_min + 3, 11]))
        st.markdown("----------------------------------------------------------")
        # CI film n°5
        st.markdown(
            "<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 4, 0]) + " (" + \
            str(reco.iloc[display_min + 4, 1]) + ")" "</h2>", unsafe_allow_html=True)
        st.markdown('<p align="center"><img width="150" height="220" src=' + parsed_list[4] + "</p>", unsafe_allow_html=True)
        st.write('Réalisateur : ' + str(reco.iloc[display_min + 4, 8]))
        st.write(
            'Acteurs principaux : ' + str(reco.iloc[display_min + 4, 9]) + ', ' + str(reco.iloc[display_min + 4, 10]))
        st.write('Synopsis : ' + str(reco.iloc[display_min + 4, 11]))
        st.markdown("----------------------------------------------------------")

    else:
        st.error("Désolé mais ta requête n'a pu aboutir. Elargis tes critères !")

if vue == 'Administrateur':
    st.sidebar.image('https://github.com/KoxNoob/Recommandation-Films-WCS/blob/master/image2.png?raw=true', width=300)
    st.sidebar.title("Menu Administrateur")
    admin = st.sidebar.selectbox('', ('Statistiques Générales', 'Focus sur un film'), 0)
    if admin == 'Statistiques Générales':
        @st.cache(persist=True)
        def csv(path):
            df_movies = pd.read_csv(path)
            df_movies.drop(['Unnamed: 0'], axis=1, inplace=True)
            return df_movies


        df_movies = csv('https://raw.githubusercontent.com/KoxNoob/Recommandation-Films-WCS/master/df_movies.csv')
        pays = pd.read_csv('https://raw.githubusercontent.com/KoxNoob/Recommandation-Films-WCS/master/df_country.csv')

        # fusion avec df_movies
        df_movies = df_movies.merge(pays, how='inner', on='imdb_title_id')
        df_movies.drop(
            columns=['Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'year_y', 'duration_y', 'avg_vote'],
            inplace=True)
        df_movies.rename(columns={'year_x': 'year', 'duration_x': 'duration'}, inplace=True)

        # extraction du premier pays
        df_movies['country'].fillna(value='unknown', inplace=True)

        c1 = []
        for index, value in df_movies['country'].items():
            x = value.split(',')
            z = x[0]
            z = z.rstrip(',')
            c1.append(z)

        df_movies['country_1'] = c1
        df_movies['pays'] = c1

        # données sur les iso alpha 3 pour visualisation carte
        iso_alpha = pd.read_csv(
            'https://gist.githubusercontent.com/tadast/8827699/raw/0d1f2d2524bc2df23c92fe306956935391665b0e/countries_codes_and_coordinates.csv')
        iso_alpha = iso_alpha[['Country', 'Alpha-3 code', 'Latitude (average)', 'Longitude (average)']]
        iso_alpha = iso_alpha.apply(lambda x: x.str.rstrip('"'))
        iso_alpha = iso_alpha.apply(lambda x: x.str.lstrip(' "'))
        iso_alpha['Latitude (average)'] = iso_alpha['Latitude (average)'].astype('float')
        iso_alpha['Longitude (average)'] = iso_alpha['Longitude (average)'].astype('float')

        for index, value in df_movies['country_1'].items():
            if value == 'USA':
                df_movies['country_1'].iat[index] = 'United States'
            if value == 'UK':
                df_movies['country_1'].iat[index] = 'United Kingdom'
            if value == 'East Germany' or value == 'West Germany':
                df_movies['country_1'].iat[index] = 'Germany'
            if value == 'Soviet Union':
                df_movies['country_1'].iat[index] = 'Russian Federation'
            if value == 'Isle Of Man':
                df_movies['country_1'].iat[index] = 'Isle of Man'
            if value == 'Czechoslovakia':
                df_movies['country_1'].iat[index] = 'Czech Republic'
            if value == 'Iran':
                df_movies['country_1'].iat[index] = 'Iran, Islamic Republic of'
            if value == 'Palestine':
                df_movies['country_1'].iat[index] = 'Palestinian Territory, Occupied'
            if value == 'Yugoslavia':
                df_movies['country_1'].iat[index] = 'Serbia'
            if value == 'The Democratic Republic Of Congo':
                df_movies['country_1'].iat[index] = 'Congo, the Democratic Republic of the'
            if value == 'Federal Republic of Yugoslavia':
                df_movies['country_1'].iat[index] = 'Montenegro'
            if value == 'North Korea':
                df_movies['country_1'].iat[index] = "Korea, Democratic People's Republic of"
            if value == 'Republic of Macedonia':
                df_movies['country_1'].iat[index] = 'Macedonia, the former Yugoslav Republic of'
            if value == 'Syria':
                df_movies['country_1'].iat[index] = 'Syrian Arab Republic'

        # fusion avec pays
        df_movies = df_movies.merge(iso_alpha, how='left', left_on='country_1', right_on='Country')

        # supression du doublon
        df_movies.drop(columns='Country', inplace=True)

        st.markdown("<h2 style='text-align: center; color: black; size = 0'>Quelques statistiques générales</h2>",
                    unsafe_allow_html=True)
        # Pie chart de la répartition des films par genre
        stat_gene = st.sidebar.selectbox("Statistiques à afficher",
                                         ("Répartition des films par genre", "Production cinématographique"))
        if stat_gene == "Répartition des films par genre":
            movies_genre = pd.DataFrame(df_movies.groupby(['genre 1'])['imdb_title_id'].count()).reset_index()
            movies_genre.rename(columns={'genre 1': 'Genre', 'imdb_title_id': 'Nombre de films'}, inplace=True)
            movies_genre['Sous_genre'] = movies_genre['Genre']
            movies_genre.loc[movies_genre['Nombre de films'] < 1000, 'Genre'] = "Divers"
            fig = px.pie(movies_genre, values='Nombre de films', names='Genre', title='Répartition des films par genre',
                         color_discrete_sequence=px.colors.sequential.Reds_r, template="plotly_dark")
            fig.update_layout(title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, showlegend=False)
            fig.update_traces(textposition='inside', textinfo='label+percent')
            st.plotly_chart(fig, use_container_width=True)

            fig = px.pie(movies_genre[movies_genre['Genre'] == 'Divers'], values='Nombre de films', names='Sous_genre',
                         title='Répartition des genres dans les films classés "Divers"',
                         color_discrete_sequence=px.colors.sequential.Reds_r, template="plotly_dark")
            fig.update_layout(title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, showlegend=False)
            fig.update_traces(textposition='inside', textinfo='label+percent')
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Bar chart sur l'évolution de la production cinématographique annuelle
            moviesByYear = pd.DataFrame(df_movies.groupby(['year'])['imdb_title_id'].count())
            moviesByYear.reset_index(inplace=True)
            moviesByYear.rename(columns={'year': 'Année', 'imdb_title_id': 'Nombre de films'}, inplace=True)
            fig = px.bar(moviesByYear, x='Année', y='Nombre de films', template="plotly_dark",
                         title='Evolution de la production cinématographique annuelle')
            fig.update_traces(marker_color='red')
            fig.update_layout(title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 24}},
                              yaxis_title="nombre de films",
                              xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

            # Map 3D sur le nombre de films par pays
            moviesByCountry = pd.DataFrame(df_movies.groupby(['Alpha-3 code', 'pays'])['imdb_title_id'].count())
            moviesByCountry.rename(columns={'imdb_title_id': 'Nombre de films'}, inplace=True)
            moviesByCountry.reset_index(inplace=True)

            fig = px.scatter_geo(moviesByCountry, title='Production cinématographique mondiale',
                                 locations="Alpha-3 code",
                                 size="Nombre de films", size_max=60, template="plotly_dark", hover_name="pays",
                                 projection="orthographic")

            fig.update_layout(title={'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, showlegend=True,
                              width=600,
                              height=600, font=dict(color='white', size=17))

            fig.update_geos(showcountries=True, countrycolor="#292929", coastlinecolor="grey")

            fig.update_traces(marker=dict(color='red'))
            st.plotly_chart(fig, use_container_width=True)

    if admin == 'Focus sur un film':
        @st.cache(persist=True)
        def csv(path):
            df_movies = pd.read_csv(path)
            df_movies.drop(['Unnamed: 0'], axis=1, inplace=True)
            return df_movies


        df_movies = csv('https://raw.githubusercontent.com/KoxNoob/Recommandation-Films-WCS/master/df_movies.csv')


        @st.cache(persist=True)
        def api_request(snip):
            url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/" + snip
            headers = {
                'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com",
                'x-rapidapi-key': "deaf55a4eemsh7c2792b225d2a3cp123471jsn98f0d82fd8f8"
            }
            response = requests.request("GET", url, headers=headers)
            return (response.text)


        @st.cache(persist=True)
        def token(string):
            start = 0
            i = 0
            token_list = []
            for x in range(0, len(string)):
                if '"' == string[i:i + 1][0]:
                    token_list.append(string[start:i + 1])
                    start = i + 1
                i += 1
            token_list.append(string[start:i + 1])
            return token_list[27]


        @st.cache(persist=True)
        def cleaner(parsed):
            parsed = parsed.replace('poster', '')
            parsed = parsed.replace('"', '')
            parsed = parsed.replace(',', '')
            parsed = parsed.replace('\\', '')
            parsed = parsed.lstrip(':')
            return parsed


        @st.cache(persist=True)
        def list_parser_bis(liste):
            url_list = []
            for i in range(len(liste)):
                raw = api_request(liste[i])
                parsed = token(raw)
                clean_url = cleaner(parsed)
                url_list.append(clean_url)
            for x in range(1, len(url_list) + 1):
                if url_list[x - 1] != "":
                    globals()['poster%s' % x] = url_list[x - 1]
                else:
                    globals()[
                        'poster%s' % x] = "https://github.com/KoxNoob/Recommandation-Films-WCS/blob/master/image.png?raw=true"
            return url_list, poster1, poster2, poster3


        # Focus sur un film
        title = st.text_input('Rentrez un titre de film', 'Deadpool')
        top3 = st.sidebar.selectbox("Affichage", ("Généralités", "Top 3 de la même année", "Top 3 du même genre"))
        if top3 == "Généralités":

            # Durée du film
            mov_imdb = df_movies[df_movies['title'] == title]['imdb_title_id'].values[0]
            mov_duree = df_movies[df_movies['imdb_title_id'] == mov_imdb]['duration'].values[0]

            fig, ax = plt.subplots(figsize=(10, 3))
            x = 0
            y = 0
            circle = plt.Circle((x, y), radius=1, facecolor='black', edgecolor=(1, 0, 0), linewidth=3)
            ax.add_patch(circle)
            label = ax.annotate(mov_duree, xy=(x, y), fontsize=45, ha="center", va='center', color='white')
            plt.title('Durée (min)', fontsize=20,
                      fontdict={'verticalalignment': 'baseline', 'horizontalalignment': 'center', 'color': 'black'})
            ax.set_aspect('equal')
            ax.autoscale_view()
            plt.axis('off')
            st.pyplot(fig)

            # Notes du film sélectionné par sexe et par tranches d'âge
            m_18 = df_movies[df_movies['title'] == title]['males_18age_avg_vote'].values[0]
            m_30 = df_movies[df_movies['title'] == title]['males_30age_avg_vote'].values[0]
            m_45 = df_movies[df_movies['title'] == title]['males_45age_avg_vote'].values.astype(int)[0]

            f_18 = df_movies[df_movies['title'] == title]['females_18age_avg_vote'].values[0]
            f_30 = df_movies[df_movies['title'] == title]['females_30age_avg_vote'].values[0]
            f_45 = df_movies[df_movies['title'] == title]['females_45age_avg_vote'].values[0]

            avg = df_movies[df_movies['title'] == title]['average_votes'].values[0]

            labels = ['18-30', '30-45', '45 +']
            men_means = [m_18, m_30, m_45]
            women_means = [f_18, f_30, f_45]

            fig = go.Figure(data=[
                go.Bar(name='Hommes', x=labels, y=men_means, marker_color='white', text=men_means,
                       textposition='outside'),
                go.Bar(name='Femmes', x=labels, y=women_means, marker_color='red', text=women_means,
                       textposition='outside')
            ])

            fig.update_layout(template="plotly_dark",
                              title_text='Note moyennne en fonction du genre et de la classe d\'âge',
                              title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'})

            # Change the bar mode
            fig.update_layout(barmode='group', width=500, height=400)
            fig.update_yaxes(range=[0, 10])
            st.plotly_chart(fig, use_container_width=True)

        elif top3 == "Top 3 du même genre":
            # TOP 3 des films du même genre

            mov_imdb = df_movies[df_movies['title'] == title]['imdb_title_id'].values[0]
            mov_id = df_movies[df_movies['title'] == title].index.values.astype(int)[0]
            mov_genre1 = df_movies[df_movies.index == mov_id]['genre 1'].values[0]
            Top_genre = df_movies[df_movies['genre 1'] == mov_genre1][
                ['imdb_title_id', 'title', 'director', 'year', 'average_votes', 'actor_1', 'actor_2',
                 'description']].sort_values(by='average_votes',
                                             ascending=False).head(3).reset_index(drop=True)
            Top_genre.index = Top_genre.index + 1
            Top_genre.rename(
                columns={'title': 'Titre', 'director': 'Réalisateur', 'year': 'Année', 'average_votes': 'Note'},
                inplace=True)
            parsed_list, poster1, poster2, poster3 = list_parser_bis(list(Top_genre['imdb_title_id'].unique()))
            st.markdown('## Top 3 des films du même genre : ' + str(mov_genre1))
            fig = go.Figure(data=[go.Table(columnorder=[1, 2, 3, 4, 5],
                                           columnwidth=[8, 50, 50, 20, 10],
                                           header=dict(values=['', 'Titre', 'Réalisateur', 'Année', 'Note'],
                                                       fill_color='red',
                                                       line=dict(width=2), font=dict(color='white', size=14)),
                                           cells=dict(
                                               values=[[1, 2, 3], Top_genre.Titre, Top_genre.Réalisateur,
                                                       Top_genre.Année,
                                                       Top_genre.Note],
                                               fill_color=['red', 'black'], line=dict(width=2),
                                               font=dict(color='white'),
                                               height=30))])

            fig.update_layout(width=1200, height=200, margin=dict(l=20, r=20, t=0, b=0, pad=0))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("----------------------------------------------------------")
            st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_genre.iloc[0, 1]) + " (" + \
                        str(Top_genre.iloc[0, 3]) + ")" "</h2>", unsafe_allow_html=True)
            st.markdown('<p align="center"><img width="150" height="220" src=' + poster1 + "</p>",
                        unsafe_allow_html=True)
            st.write('Réalisateur : ' + str(Top_genre.iloc[0, 2]))
            st.write('Acteurs principaux : ' + str(Top_genre.iloc[0, 5]) + ', ' + str(Top_genre.iloc[0, 6]))
            st.write('Synopsis : ' + str(Top_genre.iloc[0, 7]))
            st.markdown("----------------------------------------------------------")
            st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_genre.iloc[1, 1]) + " (" + \
                        str(Top_genre.iloc[1, 3]) + ")" "</h2>", unsafe_allow_html=True)
            st.markdown('<p align="center"><img width="150" height="220" src=' + poster2 + "</p>",
                        unsafe_allow_html=True)
            st.write('Réalisateur : ' + str(Top_genre.iloc[1, 2]))
            st.write('Acteurs principaux : ' + str(Top_genre.iloc[1, 5]) + ', ' + str(Top_genre.iloc[1, 6]))
            st.write('Synopsis : ' + str(Top_genre.iloc[1, 7]))
            st.markdown("----------------------------------------------------------")
            st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_genre.iloc[2, 1]) + " (" + \
                        str(Top_genre.iloc[2, 3]) + ")" "</h2>", unsafe_allow_html=True)
            st.markdown('<p align="center"><img width="150" height="220" src=' + poster3 + "</p>",
                        unsafe_allow_html=True)
            st.write('Réalisateur : ' + str(Top_genre.iloc[2, 2]))
            st.write('Acteurs principaux : ' + str(Top_genre.iloc[2, 5]) + ', ' + str(Top_genre.iloc[2, 6]))
            st.write('Synopsis : ' + str(Top_genre.iloc[2, 7]))

        else:
            # TOP 3 des films de la même année que le film sélectionné
            mov_imdb = df_movies[df_movies['title'] == title]['imdb_title_id'].values[0]
            mov_year = df_movies[df_movies['imdb_title_id'] == mov_imdb]['year'].values[0]
            Top_year = df_movies[df_movies['year'] == mov_year][
                ['imdb_title_id', 'title', 'director', 'average_votes', 'genre 1', 'actor_1', 'actor_2',
                 'description']].sort_values(by='average_votes',
                                             ascending=False).head(
                3).reset_index(drop=True)
            Top_year.index = Top_year.index + 1
            Top_year.rename(
                columns={'title': 'Titre', 'director': 'Réalisateur', 'average_votes': 'Note', 'genre 1': 'Genre'},
                inplace=True)
            parsed_list, poster1, poster2, poster3 = list_parser_bis(list(Top_year['imdb_title_id'].unique()))
            st.markdown('## Top 3 des films de la même année : ' + str(mov_year))
            fig = go.Figure(data=[go.Table(columnorder=[1, 2, 3, 4],
                                           columnwidth=[8, 50, 50, 10],
                                           header=dict(values=['', 'Titre', 'Réalisateur', 'Note'], fill_color='red',
                                                       line=dict(width=2), font=dict(color='white', size=14)),
                                           cells=dict(
                                               values=[[1, 2, 3], Top_year.Titre, Top_year.Réalisateur, Top_year.Note],
                                               fill_color=['red', 'black'], font=dict(color='white', size=[14, 12]),
                                               line=dict(width=2), height=30))])

            fig.update_layout(width=1200, height=200, margin=dict(l=20, r=20, t=0, b=0, pad=0))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("----------------------------------------------------------")
            st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_year.iloc[0, 1]) + " (" + \
                        str(Top_year.iloc[0, 3]) + ")" "</h2>", unsafe_allow_html=True)
            st.markdown('<p align="center"><img width="150" height="220" src=' + poster1 + "</p>",
                        unsafe_allow_html=True)
            st.write('Réalisateur : ' + str(Top_year.iloc[0, 2]))
            st.write('Genre : ' + str(Top_year.iloc[0, 4]))
            st.write('Acteurs principaux : ' + str(Top_year.iloc[0, 5]) + ', ' + str(Top_year.iloc[0, 6]))
            st.write('Synopsis : ' + str(Top_year.iloc[0, 7]))
            st.markdown("----------------------------------------------------------")
            st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_year.iloc[1, 1]) + " (" + \
                        str(Top_year.iloc[1, 3]) + ")" "</h2>", unsafe_allow_html=True)
            st.markdown('<p align="center"><img width="150" height="220" src=' + poster2 + "</p>",
                        unsafe_allow_html=True)
            st.write('Réalisateur : ' + str(Top_year.iloc[1, 2]))
            st.write('Genre : ' + str(Top_year.iloc[0, 4]))
            st.write('Acteurs principaux : ' + str(Top_year.iloc[1, 5]) + ', ' + str(Top_year.iloc[1, 6]))
            st.write('Synopsis : ' + str(Top_year.iloc[1, 7]))
            st.markdown("----------------------------------------------------------")
            st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_year.iloc[2, 1]) + " (" + \
                        str(Top_year.iloc[2, 3]) + ")" "</h2>", unsafe_allow_html=True)
            st.markdown('<p align="center"><img width="150" height="220" src=' + poster3 + "</p>",
                        unsafe_allow_html=True)
            st.write('Réalisateur : ' + str(Top_year.iloc[2, 2]))
            st.write('Genre : ' + str(Top_year.iloc[0, 4]))
            st.write('Acteurs principaux : ' + str(Top_year.iloc[2, 5]) + ', ' + str(Top_year.iloc[2, 6]))
            st.write('Synopsis : ' + str(Top_year.iloc[2, 7]))
