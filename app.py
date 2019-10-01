import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd
import pickle


########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title='knn'

########### Read in the model and dataset ######
file = open('resources/final_model.pkl', 'rb')
model=pickle.load(file)
file.close()
train=pd.read_pickle('resources/train.pkl')

########### Set up the layout

app.layout = html.Div(children=[
    html.H1('K-Nearest Neighbors'),
    html.Div([
        html.Div([
            html.Div([
                html.H6('Petal Length'),
                dcc.Slider(
                    id='petal-length',
                    min=1,
                    max=8,
                    step=0.1,
                    marks={i:str(i) for i in range(1, 9)},
                    value=5
                ),
                html.Br(),
            ], className='six columns'),
            html.Div([
                html.H6('Petal Width'),
                dcc.Slider(
                    id='petal-width',
                    min=1,
                    max=8,
                    step=0.1,
                    marks={i:str(i) for i in range(1, 9)},
                    value=5
                ),
                html.Br(),
            ], className='six columns'),
            html.Br(),
        ], className='twelve columns'),
        html.Div([
            html.H6(id='message'),
            dcc.Graph(
                id='figure-1'
            ),

        ], className='twelve columns'),

    html.Br(),
    html.A('Code on Github', href='https://github.com/austinlasseter/knn_iris_plotly'),
    ])
])

######### Define Callbacks


# Message callback
@app.callback(Output('message', 'children'),
              [Input('petal-length', 'value'),
               Input('petal-width', 'value')])
def display_results(value0, value1):
    new_observation=[[value0, value1]]
    prediction=model.predict(new_observation)
    specieslist=['setosa (red)', 'versicolor (blue)', 'virginica (green)']
    species =prediction[0]
    return f'The predicted species is {specieslist[species]}'


# Figure callback
@app.callback(Output('figure-1', 'figure'),
              [Input('petal-length', 'value'),
               Input('petal-width', 'value')])
def display_figure(val0, val1):
    ########## Make a prediction & find its neighbors
    new_observation=[[val0, val1]]
    prediction=model.predict(new_observation)
    neighbors=list(model.kneighbors(new_observation)[1][0])
    df_neighbors=train.iloc[neighbors, :]

    # define colors to be used in the graphic
    brights = ['red', 'blue', 'green', 'white']
    pales = ['pink', 'lightblue', 'lightgreen']

    # define the 3 traces that go into 'data'
    trace1 = go.Scatter(
        x = train['sl'],
        y = train['pl'],
        mode = 'markers',
        marker=dict(
            color=train['species'],
            colorscale=brights[:3],)
    )
    trace0 = go.Scatter(
        x = df_neighbors['sl'],
        y = df_neighbors['pl'],
        mode = 'markers',
        marker=dict(
            size=12,
            color=brights[3],
            line=dict(
                color='darkblue',
                width=1.5),
        )
    )
    trace2 = go.Scatter(
        x = [new_observation[0][0]],
        y = [new_observation[0][1]],
        mode = 'markers',
        marker=dict(
            size=18,
            color=pales[prediction[0]],
            symbol = 'star',
            line=dict(
                color='darkblue',
                width=1.5),
        )
    )
    # combine the traces in the 'data' for the graphic
    data=[trace0, trace1, trace2]

    # define the layout of the graphic
    layout = go.Layout(
        title = 'K-Nearest Neighbors', # Graph title
        xaxis = dict(title = 'Sepal Length'), # x-axis label
        yaxis = dict(title = 'Petal Length'), # y-axis label
        hovermode ='closest' # handles multiple points landing on the same vertical
    )

    # Define and update the figure
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(
        showlegend=False,
    #     width = 800,
    #     height = 800,
        yaxis = dict(
          scaleanchor = "x",
          scaleratio = 1,
        )
    )
    fig.update_xaxes(tick0=5, dtick=1)
    fig.update_yaxes(tick0=3, dtick=1)
    return fig

############ Execute the app
if __name__ == '__main__':
    app.run_server()
