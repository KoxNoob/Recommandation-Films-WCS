# Import des librairies
import pandas as pd
import streamlit as st
import numpy as np
import time
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MultipleLocator
import requests
from sklearn.neighbors import NearestNeighbors
import plotly.express as px

sns.set()
st.sidebar.image(
    'https://github.com/KoxNoob/Recommandation-Films-WCS/blob/master/Screenshot%20from%202020-05-13%2014-30-59.png?raw=true',
    width=300)
vue = st.sidebar.radio(
    "Menu",
    ('Accueil', 'Recommandations', 'Statistiques Générales', 'Focus sur un film'), 0)

if vue == 'Accueil':
    st.markdown('<body style="background-color:black;">', unsafe_allow_html=True)
    st.image('https://github.com/KoxNoob/Recommandation-Films-WCS/blob/master/accueil_1.jpeg?raw=true', width=650)
    st.image('https://github.com/KoxNoob/Recommandation-Films-WCS/blob/master/accueil_2.jpeg?raw=true', width=650)
    st.markdown('Toi aussi tu es à court d\'idée ? Alors passe à la partie __Recommandations__, nous allons t\'aider !')
    st.markdown('</body>', unsafe_allow_html=True)
if vue == 'Recommandations':
    st.markdown("<h3 style='text-align: center; color: grey; size = 0'>Maintenant que vous êtes bien installés, il n'y a plus qu'à rentrer \
             vos préférences dans la barre de naviguation à gauche, et laisser nous faire !</h3>",
                unsafe_allow_html=True)

    attente = np.random.choice([
                                   'Tiens, et si tu allais te chercher une bière ? Ou du popcorn ? Non ? Tu as raison, tout est prêt, voici notre sélection ! ', \
                                   'Il va falloir choisir Néo. La pilule bleue, ou la pilule rouge ?', 'Il s\'appelle Juste le Blanc. Son prénom c\'est \
                            Juste, et son nom c\'est le Blanc.', 'Que la force de la recommandation soit avec toi !', 'Non pas toi Obélix, tu \
                                es tombé dedans quand tu étais petit !'])
    with st.spinner(attente):
        time.sleep(8)
    st.success('Tadam !')

    @st.cache
    def csv(path):
        df_movies = pd.read_csv(path)
        df_movies.drop(['Unnamed: 0'], axis=1, inplace=True)
        return df_movies


    df_movies = csv('https://raw.githubusercontent.com/KoxNoob/Recommandation-Films-WCS/master/df_movies.csv')

    ###### Définition des fonctions ######

    sex = st.sidebar.selectbox('Votre sexe ?',
                               ('Femme', 'Homme', 'Peu importe'),2)

    age = st.sidebar.selectbox('Dans quelle tranche d\'âge êtes vous ?',
                               ('18-29 ans', '30-44 ans', '+ de 45 ans'),2)

    genre = st.sidebar.selectbox('Quel genre de films aimez-vous ?',
                                 ('Biography', 'Drama', 'Adventure', 'History', 'Crime', 'Western', 'Fantasy', 'Comedy',
                                  'Horror', 'Family', 'Action' \
                                      , 'Romance', 'Mystery', 'Animation', 'Sci-Fi', 'Musical', 'Thriller', 'Music',
                                  'Film-Noir', 'War', 'Sport', 'Adult' \
                                      , 'Documentary'),12)

    note = st.sidebar.slider('Vous aimeriez voir les films ayant quelle note de moyenne ?', 0, 10, 7)

    values = st.sidebar.slider('Sélectionner un intervalle d\'année', 1906, 2019, (1990, 2010))
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


    @st.cache
    def api_request(snip):
        url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/" + snip
        headers = {
            'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com",
            'x-rapidapi-key': "deaf55a4eemsh7c2792b225d2a3cp123471jsn98f0d82fd8f8"
        }
        response = requests.request("GET", url, headers=headers)
        return (response.text)


    @st.cache
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


    @st.cache
    def cleaner(parsed):
        parsed = parsed.replace('poster', '')
        parsed = parsed.replace('"', '')
        parsed = parsed.replace(',', '')
        parsed = parsed.replace('\\', '')
        parsed = parsed.lstrip(':')
        return parsed


    @st.cache
    def list_parser(liste):
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
                    'poster%s' % x] = "https://raw.githubusercontent.com/KoxNoob/Recommandation-Films-WCS/master/papiers-peints-vecteur-message-de-pixel-game-over.jpg.jpg"
        return url_list, poster1, poster2, poster3, poster4, poster5


    display_min = 0
    display_max = 5
    if st.sidebar.button('Afficher les 5 suivants (valable qu\'une fois)'):
        display_min += 5
        display_max += 5

    reco = recommandation(sex, age, genre, note)
    reco.rename(columns={'title': 'Titre', 'year': 'Année', 'director': 'Réalisateur', 'average_votes': 'Note',
                         'genre 1': 'Genre', 'duration': 'Durée'}, inplace=True)
    reco['Note'] = reco['Note'].apply(lambda x: round(x))
    parsed_list, poster1, poster2, poster3, poster4, poster5 = list_parser(
        list(reco['imdb_title_id'].unique()[display_min:display_max]))
    st.image([poster1, poster2, poster3, poster4, poster5], width=126)
    reco = reco.drop(['imdb_title_id'], axis=1).reset_index(drop=True)
    reco.index = reco.index + 1

    st.write(reco.iloc[display_min:display_max, :5].style.set_properties(
        **{'background-color': 'black', 'color': 'red', 'font-weight': 'bold', 'border-color': 'red'}).set_table_styles(
        [{'selector': 'th', 'props': [('color', 'red')]}]))

# CI film n°1
    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 0, 0]) + " (" + \
                str(reco.iloc[display_min + 0, 1]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster1 +"</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(reco.iloc[display_min + 0, 8]))
    st.write('Acteurs principaux : ' + str(reco.iloc[display_min + 0, 9]) + ', ' + str(reco.iloc[display_min + 0, 10]))
    st.write('Synopsis : ' + str(reco.iloc[display_min + 0, 11]))

# CI film n°2
    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 1, 0]) + " (" + \
                str(reco.iloc[display_min + 1, 1]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster2 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(reco.iloc[display_min + 1, 8]))
    st.write('Acteurs principaux : ' + str(reco.iloc[display_min + 1, 9]) + ', ' + str(reco.iloc[display_min + 1, 10]))
    st.write('Synopsis : ' + str(reco.iloc[display_min + 1, 11]))

# CI film n°3
    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 2, 0]) + " (" + \
                str(reco.iloc[display_min + 2, 1]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster3 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(reco.iloc[display_min + 2, 8]))
    st.write('Acteurs principaux : ' + str(reco.iloc[display_min + 2, 9]) + ', ' + str(reco.iloc[display_min + 2, 10]))
    st.write('Synopsis : ' + str(reco.iloc[display_min + 2, 11]))

# CI film n°4
    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 3, 0]) + " (" + \
                str(reco.iloc[display_min + 3, 1]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster4 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(reco.iloc[display_min + 3, 8]))
    st.write('Acteurs principaux : ' + str(reco.iloc[display_min + 3, 9]) + ', ' + str(reco.iloc[display_min + 3, 10]))
    st.write('Synopsis : ' + str(reco.iloc[display_min + 3, 11]))

# CI film n°5
    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(reco.iloc[display_min + 4, 0]) + " (" + \
                str(reco.iloc[display_min + 4, 1]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster5 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(reco.iloc[display_min + 4, 8]))
    st.write('Acteurs principaux : ' + str(reco.iloc[display_min + 4, 9]) + ', ' + str(reco.iloc[display_min + 4, 10]))
    st.write('Synopsis : ' + str(reco.iloc[display_min + 4, 11]))

if vue == 'Statistiques Générales':
    @st.cache
    def csv(path):
        df_movies = pd.read_csv(path)
        df_movies.drop(['Unnamed: 0'], axis=1, inplace=True)
        return df_movies


    df_movies = csv('https://raw.githubusercontent.com/KoxNoob/Recommandation-Films-WCS/master/df_movies.csv')

    st.markdown('# Quelques Statistiques Générales')
    # Pie chart de la répartition des films par genre
    movies_genre = pd.DataFrame(df_movies.groupby(['genre 1'])['imdb_title_id'].count()).reset_index()
    movies_genre.rename(columns={'genre 1': 'Genre', 'imdb_title_id': 'Nombre de films'}, inplace=True)
    fig = px.pie(movies_genre, values='Nombre de films', names='Genre',
                 title='Répartition du nombre de films par genre', color_discrete_sequence=px.colors.sequential.Reds_r)
    fig.update_layout(title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, showlegend=False)
    fig.update_traces(textposition='inside')
    st.plotly_chart(fig, use_container_width=True)

    # Var chart sur l'évolution de la production cinématographique annuelle
    moviesByYear = pd.DataFrame(df_movies.groupby(['year'])['imdb_title_id'].count())
    moviesByYear.reset_index(inplace=True)
    moviesByYear.rename(columns={'year': 'Année', 'imdb_title_id': 'Nombre de films'}, inplace=True)
    fig = px.bar(moviesByYear, x='Année', y='Nombre de films', template="plotly_dark",
                 title='Evolution de la production cinématographique annuelle')
    fig.update_traces(marker_color='red')
    fig.update_layout(title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, yaxis_title="nombre de films",
                      xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

if vue == 'Focus sur un film':
    @st.cache
    def csv(path):
        df_movies = pd.read_csv(path)
        df_movies.drop(['Unnamed: 0'], axis=1, inplace=True)
        return df_movies


    df_movies = csv('https://raw.githubusercontent.com/KoxNoob/Recommandation-Films-WCS/master/df_movies.csv')


    @st.cache
    def api_request(snip):
        url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/" + snip
        headers = {
            'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com",
            'x-rapidapi-key': "deaf55a4eemsh7c2792b225d2a3cp123471jsn98f0d82fd8f8"
        }
        response = requests.request("GET", url, headers=headers)
        return (response.text)


    @st.cache
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


    @st.cache
    def cleaner(parsed):
        parsed = parsed.replace('poster', '')
        parsed = parsed.replace('"', '')
        parsed = parsed.replace(',', '')
        parsed = parsed.replace('\\', '')
        parsed = parsed.lstrip(':')
        return parsed


    @st.cache
    def list_parser(liste):
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
                    'poster%s' % x] = "https://raw.githubusercontent.com/KoxNoob/Recommandation-Films-WCS/master/papiers-peints-vecteur-message-de-pixel-game-over.jpg.jpg"
        return url_list, poster1, poster2, poster3


    # Focus sur un film
    title = st.text_input('Rentrez un titre de film', 'Deadpool')

    # Durée du film
    mov_imdb = df_movies[df_movies['title'] == title]['imdb_title_id'].values[0]
    mov_duree = df_movies[df_movies['imdb_title_id'] == mov_imdb]['duration'].values[0]
    fig, ax = plt.subplots()
    x = 0
    y = 0
    circle = plt.Circle((x, y), radius=1, facecolor='black', edgecolor=(1, 0, 0), linewidth=3)
    ax.add_patch(circle)
    label = ax.annotate(mov_duree, xy=(x, y), fontsize=45, ha="center", va='center', color='white')
    plt.title('Durée (min)', fontsize=20, fontdict={'verticalalignment': 'baseline', 'horizontalalignment': 'center'})
    ax.set_aspect('equal')
    ax.autoscale_view()
    plt.axis('off')
    st.pyplot(fig, use_container_width=True)

    # Notes du film sélectionné par sexe et par tranches d'âge
    st.markdown('### Note moyenne en fonction du genre et de la classe d\'âge')
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

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width / 2, men_means, width, label='Hommes', color='white', edgecolor='black')
    rects2 = ax.bar(x + width / 2, women_means, width, label='Femmes', color='#db0000', edgecolor='black')

    # Add some text for labels, title and custom x-axis tick labels, etc.

    ax.set_ylabel('Note')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc=(1.04, 0))
    ax.set_ylim(0, 10)


    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', color='white')


    # ax.axhline(y=avg, linewidth=2, color='y')

    autolabel(rects1)
    autolabel(rects2)

    ax.patch.set_facecolor('black')

    fig.tight_layout()

    st.pyplot(fig, use_container_width=True)

    import plotly.graph_objects as go



    # TOP 3 des films du même genre

    mov_imdb = df_movies[df_movies['title'] == title]['imdb_title_id'].values[0]
    mov_id = df_movies[df_movies['title'] == title].index.values.astype(int)[0]
    mov_genre1 = df_movies[df_movies.index == mov_id]['genre 1'].values[0]
    Top_genre = df_movies[df_movies['genre 1'] == mov_genre1][
        ['imdb_title_id', 'title', 'director', 'year', 'average_votes', 'actor_1', 'actor_2', 'description']].sort_values(by='average_votes',
         ascending=False).head(3).reset_index(drop=True)
    Top_genre.index = Top_genre.index + 1
    Top_genre.rename(columns={'title': 'Titre', 'director': 'Réalisateur', 'year': 'Année', 'average_votes': 'Note'},
                     inplace=True)
    parsed_list, poster1, poster2, poster3 = list_parser(list(Top_genre['imdb_title_id'].unique()))
    st.markdown('# Top 3 des films du même genre : ' + str(mov_genre1))
    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_genre.iloc[0, 1]) + " (" + \
                str(Top_genre.iloc[0, 3]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster1 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(Top_genre.iloc[0, 2]))
    st.write('Acteurs principaux : ' + str(Top_genre.iloc[0, 5]) + ', ' + str(Top_genre.iloc[0, 6]))
    st.write('Synopsis : ' + str(Top_genre.iloc[0, 7]))

    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_genre.iloc[1, 1]) + " (" + \
                str(Top_genre.iloc[1, 3]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster2 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(Top_genre.iloc[1, 2]))
    st.write('Acteurs principaux : ' + str(Top_genre.iloc[1, 5]) + ', ' + str(Top_genre.iloc[1, 6]))
    st.write('Synopsis : ' + str(Top_genre.iloc[1, 7]))

    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_genre.iloc[2, 1]) + " (" + \
                str(Top_genre.iloc[2, 3]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster3 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(Top_genre.iloc[2, 2]))
    st.write('Acteurs principaux : ' + str(Top_genre.iloc[2, 5]) + ', ' + str(Top_genre.iloc[2, 6]))
    st.write('Synopsis : ' + str(Top_genre.iloc[2, 7]))

    # TOP 3 des films de la même année que le film sélectionné

    mov_year = df_movies[df_movies['imdb_title_id'] == mov_imdb]['year'].values[0]
    Top_year = df_movies[df_movies['year'] == mov_year][
        ['imdb_title_id', 'title', 'director', 'average_votes', 'genre 1', 'actor_1', 'actor_2', 'description']].sort_values(by='average_votes',
                                                                                        ascending=False).head(
        3).reset_index(drop=True)
    Top_year.index = Top_year.index + 1
    Top_year.rename(columns={'title': 'Titre', 'director': 'Réalisateur', 'average_votes': 'Note', 'genre 1': 'Genre'},
                    inplace=True)
    parsed_list, poster1, poster2, poster3 = list_parser(list(Top_year['imdb_title_id'].unique()))

    st.markdown('# Top 3 des films de la même année : ' + str(mov_year))
    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_year.iloc[0, 1]) + " (" + \
                str(Top_year.iloc[0, 3]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster1 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(Top_year.iloc[0, 2]))
    st.write('Genre : ' + str(Top_year.iloc[0,4]))
    st.write('Acteurs principaux : ' + str(Top_year.iloc[0, 5]) + ', ' + str(Top_year.iloc[0, 6]))
    st.write('Synopsis : ' + str(Top_year.iloc[0, 7]))

    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_year.iloc[1, 1]) + " (" + \
                str(Top_year.iloc[1, 3]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster2 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(Top_year.iloc[1, 2]))
    st.write('Genre : ' + str(Top_year.iloc[0,4]))
    st.write('Acteurs principaux : ' + str(Top_year.iloc[1, 5]) + ', ' + str(Top_year.iloc[1, 6]))
    st.write('Synopsis : ' + str(Top_year.iloc[1, 7]))

    st.markdown("<h2 style='text-align: center; color: red; size = 0'>" + str(Top_year.iloc[2, 1]) + " (" + \
                str(Top_year.iloc[2, 3]) + ")" "</h2>", unsafe_allow_html=True)
    st.markdown('<p align="center"><img width="150" height="220" src=' + poster3 + "</p>", unsafe_allow_html=True)
    st.write('Réalisateur : ' + str(Top_year.iloc[2, 2]))
    st.write('Genre : ' + str(Top_year.iloc[0,4]))
    st.write('Acteurs principaux : ' + str(Top_year.iloc[2, 5]) + ', ' + str(Top_year.iloc[2, 6]))
    st.write('Synopsis : ' + str(Top_year.iloc[2, 7]))
