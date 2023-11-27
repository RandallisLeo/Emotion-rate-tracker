import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
from datetime import date, timedelta
import os


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SUPERHERO],meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])
app.title = "Emotion Rate Tracker"

server = app.server

hr_data = os.path.join(os.path.dirname(os.path.abspath(__file__)),r"C:\Users\randall\Desktop\heart rate data\数据处理\1103\1105\New-HR-data-2021-12-08 20_37_23.csv")
notes_data = os.path.join(os.path.dirname(os.path.abspath(__file__)),r"C:\Users\randall\Desktop\heart rate data\数据处理\1103\1105\New-notes.csv")

df = pd.read_csv(notes_data)

df1 = pd.read_csv(hr_data)

df1.dropna(inplace=True)

df1['Date'] = pd.to_datetime(df1['Time']).dt.date
df1['Time'] = pd.to_datetime(df1['Time']).dt.time


df['mood'] = df['mood'].str.strip()

moods_list = {
    'sad': '☹️',
    'neutral': '😐',
    'happy': '😃',
    'angry': '😡',
    'fear': '😨',
    'surprise': '😮',
    'disgust': '🤢',
}

df['emojis'] = df['mood'].map(moods_list).fillna('')  

app.layout = dbc.Container(
    [
        html.H1(["Emotion Rate Tracker"], style={'text-align': 'center'}),
        html.Hr(),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(html.H3(['Hourly Activity'], style={'text-align': 'center'})),
                        dbc.Row(id='card-content', style={'overflow': 'scroll', 'overflow-x': 'hidden', 'height': '800px'})
                    ],
                    style={'margin-bottom': '50px'}, align='center', md=2
                ),

                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.DatePickerSingle(
                                            id='my-date-picker-single',
                                            min_date_allowed=date(2021, 9, 2),
                                            max_date_allowed=date(2021, 9, 19),
                                            initial_visible_month=date(2021, 9, 1),
                                            date=date(2021, 9, 10)
                                        ),
                                        html.Div(id='output-container-date-picker-single')
                                    ],
                                    md=10
                                ),
                                dbc.Col(
                                    dbc.Button("Most Frequent Mood", id="open-modal", color="primary"),
                                    style={'text-align': 'right'}
                                )
                            ],
                            align='center'
                        ),
                        dbc.Row(id='graph')
                    ],
                    align='center', md=10
                )
            ]
        ),

        dbc.Modal(
            [
                dbc.ModalHeader("Most Frequent Mood"),
                dbc.ModalBody("This is the most frequent mood", id="modal-body"),
            ],
            id="modal",
            centered=True,
        )
    ],
    fluid=True
)



@app.callback(
    [Output('output-container-date-picker-single', 'children'),Output('graph','children'),Output('card-content','children')],
    [Input('my-date-picker-single', 'date')]
)

def update_output(date_value):

    df1['Date'] = df1['Date'].astype('str')
    df1['Time'] = df1['Time'].astype('str')

    df_filtered = df[df['full_date'] == date_value]
    df1_filtered = df1[df1['Date'] == date_value]
    df_filtered['emojis'] = df_filtered['mood'].map(moods_list).fillna('')


    df_filtered['full_date'] = pd.to_datetime(df_filtered['full_date'] + ' ' + df_filtered['time'])
    df_filtered['full_date'] = pd.to_datetime(df_filtered['full_date']) - timedelta(hours=0) 
    df_filtered.sort_values('full_date',inplace=True)
    df_filtered.reset_index(inplace=True,drop=True)


    df1_filtered['Date'] = pd.to_datetime(df1_filtered['Date'] + ' ' + df1_filtered['Time'])
    df1_filtered['Date'] = pd.to_datetime(df1_filtered['Date'])
    df1_filtered.sort_values('Date',inplace=True)
    df1_filtered.reset_index(drop=True,inplace=True)

    string_prefix = 'You have selected: '
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime('%B %d, %Y')

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df1_filtered['Date'], y=df1_filtered['Empatica.mean'],
                            mode='lines', line=dict(color='#faa47f') ))

        fig.update_layout(title_text='Heart Rate',title_font_size=24,font_color='#ffffff',paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=0,r=0))

        fig.update_xaxes(showline=True, linewidth=1, linecolor='rgba(255,255,255,0.5)', showgrid=False, zeroline=False, rangeslider_visible=True)
        fig.update_yaxes(showline=True, linewidth=1, linecolor='rgba(255,255,255,0.5)', showgrid=False, zeroline=False)


        for i in range(len(df_filtered)):
            emoji = df_filtered['emojis'][i]
            if emoji:  
                fig.add_vline(x=datetime.datetime.strptime(str(df_filtered['full_date'][i]), "%Y-%m-%d %H:%M:%S").timestamp() * 1000, line_width=1, line_dash="dash", line_color="#32fbe2",annotation_text=emoji,annotation_position='top', annotation_font_size=32,annotation_hovertext=df_filtered['mood'][i])
        



        
        print(df['mood'].head())  
        df['emojis'] = df['mood'].map(moods_list)
        print(df[['mood', 'emojis']].head())  


        card_content = []

        for i in range(len(df_filtered)):
            card_content.append(dbc.Row(
                    [
                    dbc.Col(dbc.Card(children=[
                                               dbc.CardHeader(children=[df_filtered['time'][i]]),
                                               dbc.CardBody(
                                                   [
                                                       html.P(children=[df_filtered['note'][i]],
                                                             className="card-text",
                                                       ),
                                                   ]
                                               )
                                               ],style={'margin':'10px 0px 10px 10px'},color="primary", inverse=True
                                    )
                            )


                    ]
            ))

        return [string_prefix + date_string,dcc.Graph(figure=fig),card_content]

@app.callback(
    [Output("modal", "is_open"), 
     Output("modal-body", "children"), 
     Output("modal", "style")],
    [Input("open-modal", "n_clicks")],
    [State("my-date-picker-single", "date")],
)
def toggle_modal(n_clicks, date_value):
    if n_clicks and date_value:
        df_filtered = df[df['full_date'] == date_value]
        most_frequent_mood = df_filtered['mood'].value_counts().idxmax()

        
        if most_frequent_mood == 'sad':
            color = '#FFF528'
            music = html.Audio(src="/assets/light music.mp3", controls=True, autoPlay=True)
        elif most_frequent_mood == 'angry':
            color = '#A5F56A'
            music = html.Audio(src="/assets/light music.mp3", controls=True, autoPlay=True)
        elif most_frequent_mood == 'fear':
            color = '#2FFFE6'
            music = html.Audio(src="/assets/light music.mp3", controls=True, autoPlay=True)
        elif most_frequent_mood == 'disgust':
            color = '#FF9D35'
            music = html.Audio(src="/assets/light music_1.mp3", controls=True, autoPlay=True)
        else:
            color = None  
            music = ''

        return True, [f"The most frequent mood today is: {most_frequent_mood}", music], {"background-color": color}

    return False, "", {}



if __name__ == "__main__":
    app.run_server(debug=False)
