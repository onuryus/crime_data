import pandas as pd
import plotly.express as px
from jupyter_dash import JupyterDash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import Dash

df = pd.read_csv('data3.csv', dtype=str)

# "DATE OCC" sütunundaki tarihleri datetime formatına çevirelim
df['DATE OCC'] = pd.to_datetime(df['DATE OCC'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')

df_sorted = df.sort_values(by='DATE OCC')
df_sorted2 = df_sorted.drop(columns=['Date Rptd'])

# CSS ve stil ayarları
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

# Dash uygulaması
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc_css])

app.layout = html.Div([

    dcc.Tabs([
        dcc.Tab([
            dcc.Markdown(id="Markdown Title", style={"text-align": "center", "width": "100%"}),
            dcc.Markdown("From the dropdown menu, you can select the year you wish to examine, and from the radio buttons, you can choose to pre-analyze the top 5 or 10 most frequent crimes"),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        options=[
                            {'label': '2020', 'value': '2020'},
                            {'label': '2021', 'value': '2021'},
                            {'label': '2022', 'value': '2022'},
                            {'label': '2023', 'value': '2023'}
                        ],
                        value='2022',
                        className="dbc",
                        id="Yıllar"
                    ), width=2
                ),
                dbc.Col(
                    dcc.RadioItems(
                        id="head",
                        options=[
                            {'label': 'First 5', 'value': 'First 5'},
                            {'label': 'First 10', 'value': 'First 10'}
                        ],
                        value='First 5'
                    ), width=2
                )
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(id="graph")), width=6),
                dbc.Col(dbc.Card(dcc.Graph(id="graph2")), width=6)
            ])
        ], label="Crime Overview"),

        dcc.Tab([
            dcc.Markdown("Using the dropdown menu, you can view the regions with the highest to lowest crime records on the left side according to the selected year, while the right side displays a heat map of this data on a map for the selected year"),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        options=[
                            {'label': '2020', 'value': '2020'},
                            {'label': '2021', 'value': '2021'},
                            {'label': '2022', 'value': '2022'},
                            {'label': '2023', 'value': '2023'}
                        ],
                        value='2022',
                        className="dbc",
                        id="Yıllar_harita"
                    ), width=2
                )
            ]),
            dbc.Row([
                dbc.Col(
                    [
                        dcc.Markdown(id="table_title", style={"text-align": "center", "width": "100%"}),
                        dbc.Table(id='area_table', striped=True, bordered=True, hover=True)
                    ], width=6
                ),
                dbc.Col(
                    [
                        dcc.Markdown(id="heatmap_title", style={"text-align": "center", "width": "100%"}),
                        html.Iframe(
                            id='folium_map',
                            srcDoc='',
                            width='100%',
                            height='600px'
                        )
                    ], width=6
                )
            ])
        ], label="Crime Overview by Areas")
    ], className="dbc")
])

@app.callback(
    [Output("Markdown Title", "children"),
     Output('graph', 'figure'),
     Output('graph2', 'figure')],
    [Input("Yıllar", "value"),
     Input("head", "value")]
)
def update_graphs(yıllar, radio):
    if not yıllar or not radio:
        raise PreventUpdate

    markdown_title = f"Crime Record Summary for {yıllar}"

    graph_yıllar = df[df['DATE OCC'].dt.year == int(yıllar)]

    if radio == "First 5":
        crime_counts = graph_yıllar['Crm Cd Desc'].value_counts().reset_index().head(5)
    elif radio == "First 10":
        crime_counts = graph_yıllar['Crm Cd Desc'].value_counts().reset_index().head(10)

    crime_counts.columns = ['Crime Type', 'Count']

    # Treemap grafiği için SLATE teması renklerine uygun hale getirme
    graph = px.treemap(
        crime_counts,
        path=['Crime Type'],
        values='Count',
        title=f'Most Committed Crime Types in {yıllar}',
        color='Count',
        width=600,
        height=600,
        labels={'Count': 'Crime Count'}
    )

    graph.update_traces(
        textinfo="label+value+percent entry",
        hoverinfo="label+value+percent entry",
        marker=dict(
            colorscale='reds'  # SLATE temasına uygun bir renk skalası seçildi
        )
    )

    graph.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font=dict(size=20, color='white', family="Lato, sans-serif"),
        margin=dict(l=0, r=0, t=50, b=0)
    )

    monthly_crime_counts = graph_yıllar.groupby([graph_yıllar['DATE OCC'].dt.to_period('M'), 'Crm Cd Desc']).size().reset_index(name='Count')
    monthly_crime_counts['Month'] = monthly_crime_counts['DATE OCC'].astype(str)
    monthly_crime_counts = monthly_crime_counts.drop(columns='DATE OCC')

    if radio == "First 5":
        top_crimes = monthly_crime_counts.groupby('Crm Cd Desc')['Count'].sum().nlargest(5).index
        top_crime_data = monthly_crime_counts[monthly_crime_counts['Crm Cd Desc'].isin(top_crimes)]
    elif radio == "First 10":
        top_crimes = monthly_crime_counts.groupby('Crm Cd Desc')['Count'].sum().nlargest(10).index
        top_crime_data = monthly_crime_counts[monthly_crime_counts['Crm Cd Desc'].isin(top_crimes)]

    graph2 = px.line(
        top_crime_data,
        x='Month',
        y='Count',
        color='Crm Cd Desc',
        title=f' Monthly Distribution of Crime Types in {yıllar}',
        labels={'Count': 'Crime Count', 'Month': 'Month', 'Crm Cd Desc': 'Crime Type'},
        markers=True
    )

    graph2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font=dict(size=20, color='white', family="Lato, sans-serif"),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.4,
            xanchor='center',
            x=0.5
        ),
        yaxis_title='Number of Crimes',
        width=600,
        height=600,
        margin=dict(l=20, r=20, t=50, b=50)
    )

    graph2.update_traces(
        line=dict(width=2),
        marker=dict(size=10, symbol='circle')
    )

    return markdown_title, graph, graph2

@app.callback(
    [Output('folium_map', 'srcDoc'),
     Output('area_table', 'children'),
     Output('table_title', 'children'),
     Output('heatmap_title', 'children')],
    [Input("Yıllar_harita", "value")]
)
def update_map_and_table(yıllar):
    heatmap_filename = f'la_heatmap{yıllar}.html'

    try:
        with open(heatmap_filename, 'r') as file:
            heatmap_src = file.read()
    except FileNotFoundError:
        heatmap_src = "<p>Harita bulunamadı.</p>"

    # Tabloyu güncelleme
    area_counts = df[df['DATE OCC'].dt.year == int(yıllar)]['AREA NAME'].value_counts().reset_index()
    area_counts.columns = ['AREA NAME', 'Count']

    table = dbc.Table.from_dataframe(
        area_counts,
        striped=True,
        bordered=True,
        hover=True,
        class_name="dbc"
    )

    table_title = f" Crime Table for {yıllar} "
    heatmap_title = f"Heatmap for {yıllar}"

    return heatmap_src, table, table_title, heatmap_title

if __name__ == '__main__':
    app.run_server(debug=True)
