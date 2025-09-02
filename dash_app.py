import dash                                         # Web framework
from dash import dcc                                # Web interactive components
from dash import html                               # Web HTML
from dash.dependencies import Input, Output, State  # Inputs and Outputs
import pandas as pd                                 # Library for manipulating data like graphs
from datetime import datetime, timedelta            # Uses operations of Dates and Times
import plotly.graph_objects as go                   # Creates Pot charts and graphs

#---------------------------------------------------------------------------------------O

#-----------------------------------FUNCTION: LOAD DATA--------------------------------------------------------------------------------O

# load_data reads data from csv file and processes it through DataFrame
# Function to load data
def load_data(filename, start_row=0, num_rows=None, end_time=None, start_time=None):
    column_names = [
        "CO2", "Humidity", "Chamber", "Pad", "Thermistor1",
        "Thermistor2", "Pad Duty", "Valve Duty", "Pad Power", "Water Level"
    ]
    
    # Read the dataset without headers
    if num_rows is None:
        df = pd.read_csv(filename, header=None, names=column_names, on_bad_lines='skip')
    else:
        df = pd.read_csv(filename, header=None, names=column_names, on_bad_lines='skip', skiprows=start_row, nrows=num_rows)
    df = df.apply(pd.to_numeric, errors='coerce')
    df.replace(0, pd.NaT, inplace=True)
    
    # Create a time series starting from a specific time and going forwards every second
    time_index = pd.date_range(start=start_time, periods=len(df), freq='s')
    df.index = time_index
    
    if end_time is not None:
        df = df[df.index <= end_time]
    
    return df

#----------------------------------------------------------------------------------------------------------------------------O

#-----------------------------------LOAD DATA--------------------------------------------------------------------------------O

# Starts the time range and load data from the CSV file into the DataFrame
# Also CALCULATES the TOTAL NUMBER OF ROWS AND RECIEVES LAST DATA POINT FROM EACH COLUMN
# Load data
end_time = datetime(2024,4,19,1,45,0)
start_time = datetime(2024,4,18,13,45,0)
total_rows = len(load_data('041924_1.TXT', start_time=start_time))
df = load_data('041924_1.TXT', end_time=end_time, start_time=start_time)
last_row = len(df)
curr_time = 0
# Get the last data point of each column
last_data_points = df.iloc[-1]

#----------------------------------------------------------------------------------------------------------------------------O

#-----------------------------------SETTING UP-------------------------------------------------------------------------------O

# Setting up the App with CSS stylesheet and defines title of dashboard
# Also Sets up the units for data columns
# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=['assets/styles.css'])

app.config.suppress_callback_exceptions = True

# Set the title
app.title = "Mini-cluster Dashboard"

units = {
    'CO2': '%',
    'Humidity': '%',
    'Chamber': '°C',
    'Pad': '°C',
    'Thermistor1': '°C',
    'Thermistor2': '°C',
}

#----------------------------------------------------------------------------------------------------------------------------O

#-----------------------------------LAYOUT/DEFINING-------------------------------------------------------------------------------O

# Defines the structure of the app with HTML and Dash including:
# Header, current DD menus, historical data and component for periodic updates
# Define the layout of the app
app.layout = html.Div([
    html.Div([
        html.H1("My Dashboard", style={
            'flex': '1',
            'textAlign': 'left', 
            'paddingLeft': '50px',
            'color': 'white'
        }),
        html.H3(f"Last updated: {df.index[-1].strftime('%Y-%m-%d %H:%M:%S')}", id='last-updated', style={
            'flex': '2',
            'textAlign': 'right', 
            'paddingRight': '50px',
            'color': 'white',
            'paddingTop': '15px'
        })
    ], style={
        'display': 'flex',
        'position': 'fixed', 
        'top': 0, 
        'width': '100vw', 
        'backgroundColor': 'green',
        'zIndex': 1000,
    }),
    
    html.Div([
        html.Label('Current Data:', style={'display': 'inline-block', 'marginRight': '10px', 'marginLeft': '20px'}),
        dcc.Dropdown(
            id='current-data-dropdown',
            options=[{'label': 'Show', 'value': 'show'}, {'label': 'Hide', 'value': 'hide'}],
            value='show',
            style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'middle'}
        ),
        html.Div(id='data-modules'),
        
        # Add the toggle button here
        html.Button('Toggle Dynamic/Static', id='toggle-button', n_clicks=0, style={'marginTop': '10px'}),
    ], style={'marginTop': '100px'}),
    
    html.Div([
        html.Label('Historical Data:', style={'display': 'inline-block', 'marginRight': '10px', 'marginLeft': '20px'}),
        dcc.Dropdown(
            id='historical-data-dropdown',
            options=[{'label': 'Show', 'value': 'show'}, {'label': 'Hide', 'value': 'hide'}],
            value='hide',
            style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'middle'}
        ),
        html.Div([
            dcc.Loading(
                id='loading',
                type='default',
                children=html.Div(id='historical-data-div')
            ),
        ]),
    ], style={'marginTop': '20px'}),
    
    html.Div([
        html.Label('Select Date:', style={'display': 'inline-block', 'marginRight': '10px', 'marginLeft': '20px'}),
        dcc.DatePickerSingle(
            id='date-picker',
            min_date_allowed=start_time.date(),
            max_date_allowed=end_time.date(),
            date=start_time.date(),
            display_format='YYYY-MM-DD',
            style={'display': 'inline-block', 'verticalAlign': 'middle'}
        ),
        html.Div(id='selected-date-data')
    ], style={'marginTop': '20px'}),
    
    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    ),
    
    dcc.Store(id='data-mode', data='dynamic'),
    dcc.Store(id='df-update-flag', storage_type='session', data=0),
    
    # Add the download button and the Download component here
    html.Button('Download Data', id='download-button', style={'marginTop': '20px'}),
    dcc.Download(id='download-selected-date-dataframe-csv'),
    
    html.Div([
        html.Label('Select Date for Download:', style={'display': 'inline-block', 'marginRight': '10px', 'marginLeft': '20px'}),
        dcc.DatePickerSingle(
            id='download-date-picker',
            min_date_allowed=start_time.date(),
            max_date_allowed=end_time.date(),
            date=start_time.date(),
            display_format='YYYY-MM-DD',
            style={'display': 'inline-block', 'verticalAlign': 'middle'}
        ),
        html.Button('Download Selected Date Data', id='download-selected-date-button', style={'marginLeft': '10px', 'marginTop': '10px'})
    ], style={'marginTop': '20px'}),
    
], style={'fontFamily': 'Helvetica'})

#-----------------------------------UPDATE DATA-------------------------------------------------------------------------------O

# CALLBACK function updates the data by periodically loading new rows from CSV file
# Make sure new data matches structure and updates global DataFrame
@app.callback(
    [Output('interval-component', 'n_intervals'),
     Output('df-update-flag', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('data-mode', 'data')]
)
def update_data(n, mode):
    if mode == 'static':
        return n, 0
    
    global df
    global last_row
    global curr_time
    global last_data_points
    
    # Load new data
    new_df = pd.DataFrame()
    df_flag = 0
    while len(new_df) == 0 and last_row < total_rows:  # assuming total_rows is the total number of rows in your data
        new_df = load_data('041924_1.TXT', start_row=last_row, num_rows=1, start_time=df.index[-1] + timedelta(seconds=1))
        if new_df.shape[1] != df.shape[1]:
            new_df = pd.DataFrame()
        last_row += 1
        curr_time += 1
       
    print(last_row)

    if len(new_df) > 0:
        df = pd.concat([df, new_df])
        last_data_points = df.iloc[-1]
        df_flag = 1
    
    return n, df_flag

#-----------------------------------------------------------------------------------------------------------------------------------O

#-----------------------------------LAST UPDATED DATA-------------------------------------------------------------------------------O

# UPDATES the LAST UPDATED timestamp on dashboard header
@app.callback(
    Output('last-updated', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_last_updated(n):
    return f"Last updated: {df.index[-1].strftime('%Y-%m-%d %H:%M:%S')}"

#------------------------------------------------------------------------------------------------------------------------------------O

#-----------------------------------UPDATE DATA MODULES-------------------------------------------------------------------------------O

# UPDATES the display of current data modules based on chosen option from the dropdown
@app.callback(
    Output('data-modules', 'children'),
    [Input('current-data-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_data_modules(value, n):
    if value == 'show':
        return html.Div(
            [
                html.Div(
                    [
                        html.H4(column),
                        html.H2(f"{last_data_points[column]} {units.get(column, '')}")
                    ],
                    className='data-module',
                    style={
                        'backgroundColor': 'lightgrey',
                        'borderRadius': '10px',
                        'margin': '10px',
                        'padding': '10px',
                        'textAlign': 'center'
                    }
                ) for column in last_data_points.keys()
            ],
            className='data-grid',
            style={
                'marginTop': '20px',
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fill, minmax(200px, 1fr))',
                'gridGap': '10px'
            }
        )
    else:
        return None

#------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------UPDATE GRAPH-------------------------------------------------------------------------------O

# UPDATES the display of the graph based on the chosen option from the dropdown
@app.callback(
    Output('historical-data-div', 'children'),
    [Input('historical-data-dropdown', 'value')]
)
def update_graph(value):
    if value == 'show':
        return dcc.Graph(
            id='historical-data-graph',
            figure={
                'data': [
                    go.Scatter(
                        x=df.index[:curr_time],
                        y=df[column][:curr_time],
                        mode='lines',
                        name=column
                    ) for column in df.columns
                ],
                'layout': go.Layout(
                    showlegend=True
                )
            },
            style={'width': '100vw', 'height': '90vh'}
        )
    else:
        return None

#------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------UPDATE SELECTED DATE DATA-------------------------------------------------------------------------------O

# UPDATES the display of the data based on the selected date
@app.callback(
    Output('selected-date-data', 'children'),
    [Input('date-picker', 'date')]
)
def update_selected_date_data(selected_date):
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
        day_data = df[(df.index.date == selected_date.date())]
        if not day_data.empty:
            return html.Div(
                [
                    html.H3(f"Data for {selected_date.strftime('%Y-%m-%d')}"),
                    dcc.Graph(
                        id='selected-date-graph',
                        figure={
                            'data': [
                                go.Scatter(
                                    x=day_data.index,
                                    y=day_data[column],
                                    mode='lines',
                                    name=column
                                ) for column in day_data.columns
                            ],
                            'layout': go.Layout(
                                showlegend=True
                            )
                        },
                        style={'width': '100vw', 'height': '90vh'}
                    )
                ]
            )
        else:
            return html.Div(
                html.H3(f"No data available for {selected_date.strftime('%Y-%m-%d')}")
            )
    else:
        return None

#------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------TOGGLE DATA MODE-------------------------------------------------------------------------------O

# Toggles between dynamic and static data mode
@app.callback(
    Output('data-mode', 'data'),
    [Input('toggle-button', 'n_clicks')],
    [State('data-mode', 'data')]
)
def toggle_data_mode(n_clicks, current_mode):
    if n_clicks % 2 == 0:
        return 'dynamic'
    else:
        return 'static'

#------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------DOWNLOAD DATA-------------------------------------------------------------------------------O

# Callback to handle the download process
@app.callback(
    Output('download-dataframe-csv', 'data'),
    Input('download-button', 'n_clicks'),
    prevent_initial_call=True
)
def download_data(n_clicks):
    return dcc.send_data_frame(df.to_csv, "data.csv")

# Callback Output
@app.callback(
    Output('download-selected-date-dataframe-csv', 'data'),
    Input('download-selected-date-button', 'n_clicks'),
    State('download-date-picker', 'date'),
    prevent_initial_call=True
)
def download_selected_date_data(n_clicks, selected_date):
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
        day_data = df[(df.index.date == selected_date.date())]
        if not day_data.empty:
            return dcc.send_data_frame(day_data.to_csv, f"data_{selected_date.strftime('%Y-%m-%d')}.csv")

#------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------RUN APP-------------------------------------------------------------------------------O

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

#------------------------------------------------------------------------------------------------------------------------------------
