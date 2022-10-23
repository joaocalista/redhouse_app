#bibliotecas

# +--------manipulação e analise de dados
import pandas            as pd
import geopandas

# +---------visualização de dados
import plotly.express    as px
import seaborn           as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# +---------desenvolvimento web
import streamlit         as st

# +---------geocoder
import reverse_geocoder  as rg

# +---------suprime avisos
import warnings
warnings.filterwarnings("ignore")

#carrega os dados para a memoria
@st.cache( allow_output_mutation=True )
def read_data(path):
    return pd.read_csv(path)


#define as estações do ano
def season_of_year(date):
    year = str(date.year)

    seasons = {'spring': pd.date_range(start='20/03/' + year, end='20/06/' + year),
               'summer': pd.date_range(start='21/06/' + year, end='22/09/' + year),
               'fall': pd.date_range(start='23/09/' + year, end='20/12/' + year)}

    if date in seasons['spring']:
        return 'spring'
    if date in seasons['summer']:
        return 'summer'
    if date in seasons['fall']:
        return 'fall'
    else:
        return 'winter'


#realiza o tratamento dos dados
def treat_data(data):
    #deleta IDs duplicados
    data = data.sort_values(by=['id', 'date']).drop_duplicates('id', keep='last')

    #reordena index
    data.sort_index(inplace=True)

    #converte a coluna 'date' para o tipo datetime
    data['date'] = data['date'].astype('datetime64[ns]')

    #adiciona a coluna 'season_available'
    data['season_available'] = data['date'].apply(season_of_year)

    #deleta a casa que contém 33 quartos (provavelmente foi um erro de digitação)
    data.drop(data[data['bedrooms'] == 33].index[0], inplace=True)

    #agrupa dados pelo zipcode
    df = data[['price', 'zipcode']].groupby('zipcode').median().reset_index()
    df.columns = ['zipcode', 'median_price_per_zipcode']

    #mescla os dados pelo zipcode
    data = data.merge(df, on='zipcode', how='inner')

    return data


#filtra as casas que deveriam ser compradas pela empresa
def filter_houses(data):
    data.loc[(data['price'] < data['median_price_per_zipcode']) & (data['condition'] >= 3) & (
                data['grade'] >= 8), 'buy'] = 'Yes'
    data['buy'].fillna('No', inplace=True)

    data = data[data['buy'] == 'Yes']

    return data


# Verifica o preço mediano dada uma região e as estações do ano
def median_price_by_zip_season(data):
    #agrupa dados pelo zipcode e estação do ano
    df = data[['zipcode', 'season_available', 'price']].groupby(['zipcode', 'season_available']).median()
    df = df.unstack().T

    #exclui o primeiro nivel relacionado ao index
    df = df.droplevel(level=0)

    #cria dataframen contendo o zipcode da região e qual a estação que as casas deveriam ser vendidas
    zip_season = pd.DataFrame(df.idxmax()).reset_index()
    zip_season.columns = ['zipcode', 'season_to_sell']

    #cria dataframe contendo o zipcode e o preço mediano das casas levando em conta
    #a região e a estação do ano em que a casa ficou disponivel para venda
    zip_price = pd.DataFrame(df.max()).reset_index()
    zip_price.columns = ['zipcode', 'median_price_zip_season']

    #mescla as tabelas
    df = zip_season.merge(zip_price, on='zipcode')

    data = data.merge(df, on='zipcode')

    #renomeia coluna
    data.rename(columns={'price': 'buying_price'}, inplace=True)

    return data


#verifica qual o bairro/região relacionado a um determinado zipcode, através de geocoder reverso
def neighbourhood_feature(data):
    # cria coluna chamada 'location'
    data['location'] = list(zip(data.lat, data.long))

    #verifica todas as regiões relacionadas aos zipcodes
    results = rg.search(list(data['location']))
    neighbourhoods = [results[i]['name'] for i in range(len(results))]
    data['neighbourhood'] = neighbourhoods

    return data


#define o preço de venda dos imoveis
def set_sell_price(data):
    data.loc[(houses_to_buy['buying_price'] > data['median_price_zip_season']), 'sell_price'] = data[
                                                                                                    'buying_price'] * 1.10
    data.loc[(houses_to_buy['buying_price'] <= data['median_price_zip_season']), 'sell_price'] = data[
                                                                                                     'buying_price'] * 1.30
    data['sell_price/sqft'] = data['sell_price'] / data['sqft_lot']

    return data


#define o lucro obtido em cada imovel
def set_profit(data):
    # profit
    data['profit'] = data['sell_price'] - data['buying_price']

    # avg_profit/sqft
    data['profit/sqft'] = data['profit'] / data['sqft_lot']

    return data


#mostra informacoes gerais
def overall_info(raw_data,data):
    st.title('Principais Informações')
    c1, c2 = st.columns(2)

    with c1:
        st.header('💰 Financeiro')
        st.write(f'Investimento a Realizar: **$ {data["buying_price"].sum():,.2f}**')
        st.write(f'Faturamento Esperado: **$ {data["sell_price"].sum():,.2f}**')
        st.write(f'Lucro Esperado: **$ {data["profit"].sum():,.2f}**')

    with c2:
        st.header('📌 Observações Importantes')
        st.write(f'- Total de imóveis disponíveis no portfólio: **{raw_data.shape[0]}**')
        st.write(f'- Total de imóveis recomendados para compra: **{data.shape[0]}**')
        st.write('- Seattle é uma região importante para o negócio uma vez que, dentre os imóveis recomendados, ela possui um preço de compra e venda/pé² mais caro, '
                 'média de lucro/pé² maior e possui a maior quantidade de imóveis recomendados para compra.')
        st.write('- O nível de construção e projeto do edifício influencia diretamente no preço do imóvel.')

    st.markdown("""<hr>""", unsafe_allow_html=True)


#reseta os filtros
def reset_filters(buy_price_value, profit_value, sell_price_value):

    st.session_state.f_neighbourhood = []
    st.session_state.f_buy_price = buy_price_value
    st.session_state.f_profit = profit_value
    st.session_state.f_sell_price = sell_price_value
    st.session_state.f_season = []


#mostra a tabelas e mapa contendo os imoveis recomendaddos para compra
def show_data(data):

    st.sidebar.header('Filtrar Imóveis Recomendados')

    f_neighbourhood = st.sidebar.multiselect('Regiões',
                                             data['neighbourhood'].sort_values().unique(),
                                             key= 'f_neighbourhood')

    f_buy_price = st.sidebar.slider('Preço de Compra',
                                    min_value=data['buying_price'].min(),
                                    max_value=data['buying_price'].max(),
                                    value= float(data['buying_price'].max()),
                                    step=10000.0,
                                    key='f_buy_price')

    f_sell_price = st.sidebar.slider('Preço de Venda',
                                     min_value=data['sell_price'].min(),
                                     max_value=data['sell_price'].max(),
                                     value=float(data['sell_price'].max()),
                                     step=10000.0,
                                     key='f_sell_price')

    f_profit = st.sidebar.slider('Lucro',
                                 data['profit'].min(),
                                 data['profit'].max(),
                                 value= (float(data['profit'].min()), float(data['profit'].max())),
                                 step=10000.0,
                                 key='f_profit')

    f_season = st.sidebar.multiselect('Estação do Ano Para Venda',
                                      options=data['season_to_sell'].sort_values().unique(),
                                      key='f_season')

    reset_button = st.sidebar.button('Excluir Filtros',
                                     on_click=reset_filters,
                                     kwargs={'buy_price_value': data.buying_price.max(),
                                             'profit_value': (data['profit'].min(), data['profit'].max()),
                                             'sell_price_value': data['sell_price'].max()},
                                     key='reset_button')

    c1, c2 = st.columns(2)

    with c1:

        cols = [ 'id',
                 'buying_price',
                 'sell_price',
                 'profit',
                 'season_to_sell',
                 'neighbourhood',
                 'zipcode',
                 'location' ]

        st.markdown("<h1 style='text-align: center;'>Visão Geral dos Imóveis Recomendados</h1>",
                    unsafe_allow_html=True)

        if not f_neighbourhood and not f_season:
            data_filter = data[(data['buying_price'] <= f_buy_price) &
                              (data['sell_price'] <= f_sell_price) &
                              (data['profit'] >= f_profit[0]) &
                              (data['profit'] <= f_profit[1])]

            st.dataframe(data_filter[cols], height=600)

        elif f_neighbourhood and not f_season:
            data_filter = data[(data['neighbourhood'].isin(f_neighbourhood)) &
                              (data['buying_price'] <= f_buy_price) &
                              (data['sell_price'] <= f_sell_price) &
                              (data['profit'] >= f_profit[0]) &
                              (data['profit'] <= f_profit[1])]

            st.dataframe(data_filter[cols], height=600)

        elif f_neighbourhood and f_season:
            data_filter = data[(data['neighbourhood'].isin(f_neighbourhood)) &
                              (data['buying_price'] <= f_buy_price) &
                              (data['season_to_sell'].isin(f_season)) &
                              (data['sell_price'] <= f_sell_price) &
                              (data['profit'] >= f_profit[0]) &
                              (data['profit'] <= f_profit[1])]

            st.dataframe(data_filter[cols], height=600)

        else:
            data_filter = data[(data['buying_price'] <= f_buy_price) &
                              (data['sell_price'] <= f_sell_price) &
                              (data['season_to_sell'].isin(f_season)) &
                              (data['profit'] >= f_profit[0]) &
                              (data['profit'] <= f_profit[1])]

            st.dataframe(data_filter[cols], height=600)

        st.download_button('Baixar Relatório', data_filter.to_csv(index=False).encode('utf-8'),
                                   'imoveis_recomendados.csv', mime='text/csv')

    with c2:
        st.markdown("<h1 style='text-align: center;'>Distribuição dos Imóveis</h1>", unsafe_allow_html=True)

        if not f_neighbourhood and not f_season:
            distribution_map(data[(data['buying_price'] <= f_buy_price) &
                              (data['sell_price'] <= f_sell_price) &
                              (data['profit'] >= f_profit[0]) &
                              (data['profit'] <= f_profit[1])])


        elif f_neighbourhood and not f_season:
            distribution_map(data[(data['neighbourhood'].isin(f_neighbourhood)) &
                              (data['buying_price'] <= f_buy_price) &
                              (data['sell_price'] <= f_sell_price) &
                              (data['profit'] >= f_profit[0]) &
                              (data['profit'] <= f_profit[1])])

        elif f_neighbourhood and f_season:
            distribution_map(data[(data['neighbourhood'].isin(f_neighbourhood)) &
                              (data['buying_price'] <= f_buy_price) &
                              (data['season_to_sell'].isin(f_season))&
                              (data['sell_price'] <= f_sell_price) &
                              (data['profit'] >= f_profit[0]) &
                              (data['profit'] <= f_profit[1])])

        else:
            distribution_map(data[(data['buying_price'] <= f_buy_price) &
                              (data['sell_price'] <= f_sell_price) &
                              (data['season_to_sell'].isin(f_season)) &
                              (data['profit'] >= f_profit[0]) &
                              (data['profit'] <= f_profit[1])])


#mostra mapa de distribuição, relacionado ao lucro
def distribution_map(data):
    df = data[['id', 'buying_price', 'lat', 'long', 'sell_price', 'season_to_sell', 'profit', 'neighbourhood']]
    fig = px.scatter_mapbox(df,
                            lat='lat',
                            lon='long',
                            color='profit',
                            hover_name='id',
                            hover_data=['lat', 'long', 'buying_price', 'sell_price', 'season_to_sell', 'profit', 'neighbourhood'],
                            size='profit',
                            size_max=15,
                            zoom=10,
                            height=600,
                            color_continuous_scale=px.colors.sequential.Sunset)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    st.plotly_chart(fig, use_container_width=True)


#mostra mapa relacionado ao lucro/pe² para cada regiao
def profit_sqrft_map(data):

    st.markdown("<h1 style='text-align: center;'>Mapa de densidade da média do lucro por pé quadrado</h1>", unsafe_allow_html=True)

    # lendo geofile
    geofile = geopandas.read_file(
        'datasets/Zipcodes_for_King_County_and_Surrounding_Area_(Shorelines)___zipcode_shore_area.geojson')

    # Agrupando dados
    df = data[['profit/sqft', 'zipcode']].groupby('zipcode').mean().reset_index()
    df.columns = ['ZIP', 'avg_profit/sqft']

    # Unindo tabelas
    geofile = geofile.merge(df, on='ZIP', how='inner')

    # mapa base
    m = folium.Map(location=(47.5052, -121.906), zoom_start=9)

    marker_cluster = MarkerCluster().add_to(m)

    for i, row in houses_to_buy.iterrows():
        folium.Marker(location=[row.lat, row.long],
                      popup=f'ID: {row.id}\nLucro/pe²: $ {row["profit/sqft"]:.2f}\nRegião: {houses_to_buy.neighbourhood[i]}').add_to(
            marker_cluster)

    # mapa coroplético
    fig = folium.Choropleth(
        geo_data=geofile,
        data=df,
        columns=["ZIP", "avg_profit/sqft"],
        key_on="feature.properties.ZIP",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Average Profit/sqft",
    ).add_to(m)

    # adicionando pop-up ao mapa coroplético
    folium.GeoJsonTooltip(['ZIP']).add_to(fig.geojson)

    folium_static(m, height=800, width=1600)


#mostra os graficos
def show_graphs(data):
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<h4 style='text-align: center;'>Top 10 regiões com a maior quantidade de imóveis recomendados</h4>",
                    unsafe_allow_html=True)
        fig1 = sns.countplot(x='neighbourhood',
                             data=data,
                             order=data['neighbourhood'].value_counts().index[:10],
                             palette='rocket')
        plt.xticks(rotation=60)
        plt.xlabel('Região')
        plt.ylabel('Qntd de Imóveis')

        sns.despine()

        st.pyplot(fig1.figure)

    with c2:
        st.markdown("<h4 style='text-align: center;'>Top 10 regiões com a maior média do preço de venda/pé²</h4>",
                    unsafe_allow_html=True)

        df = data[['neighbourhood', 'sell_price/sqft']].groupby('neighbourhood').mean().reset_index().sort_values(
            by='sell_price/sqft', ascending=False)

        fig2 = sns.barplot(x='neighbourhood',
                    y='sell_price/sqft',
                    data=df.head(10),
                    palette='rocket')

        plt.xticks(rotation=60)
        plt.xlabel('Região')
        plt.ylabel('preço/pé² médio')

        sns.despine()

        st.pyplot(fig2.figure)


#funcao principal
if __name__ == '__main__':

    #configuracao da pagina
    st.set_page_config(page_title='RedHouse', page_icon='🏠', layout="wide", initial_sidebar_state="collapsed")

    st.markdown("<h1 style='text-align: center;'>RedHouse</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Bem-Vindo ao Relatório de Sugestão de Compra e Venda de Imóveis!</h3>", unsafe_allow_html=True)

    st.markdown("""<hr>""", unsafe_allow_html=True)

    #extract
    raw_data = read_data('datasets/kc_house_data.csv')

    #treat data
    raw_data = treat_data(raw_data)
    houses_to_buy = filter_houses(raw_data)
    houses_to_buy = median_price_by_zip_season(houses_to_buy)
    houses_to_buy = neighbourhood_feature(houses_to_buy)
    houses_to_buy = set_sell_price(houses_to_buy)
    houses_to_buy = set_profit(houses_to_buy)

    #visualization
    overall_info(raw_data, houses_to_buy)
    show_data(houses_to_buy)
    profit_sqrft_map(houses_to_buy)
    show_graphs(houses_to_buy)


