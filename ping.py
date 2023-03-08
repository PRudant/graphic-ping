import time
import ping3
import plotly.graph_objs as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from collections import deque

app = dash.Dash(__name__)

# Définir les adresses IP à pinger
ips = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.1.1.2']

# Interval de PING
intervalping = 2000
intervalps = intervalping / 1000

# Définir la file d'attente pour stocker les données de latence
latency_data = {ip: deque(maxlen=50) for ip in ips}

# Définir la mise en page de l'application
app.layout = html.Div([
    html.H1('Ping Test'),
    html.Label('Adresses IP à pinger :'),
    dcc.Input(id='ip-input', value='8.8.8.8, 8.8.4.4, 1.1.1.1, 1.1.1.2', type='text'),
    dcc.Graph(id='live-graph', figure={'data': [], 'layout': go.Layout(xaxis=dict(title='Date & Heure'), yaxis=dict(title='Latence (ms)'))}),
    dcc.Interval(
        id='graph-update',
        interval=intervalping,  # Mettre à jour toutes les secondes
        n_intervals=0
    )
])

# Définir la fonction de mise à jour du graphique
@app.callback(Output('live-graph', 'figure'), [Input('graph-update', 'n_intervals'), Input('ip-input', 'value')])
def update_graph(n, ip_input):
    # Convertir la chaîne de caractères en une liste d'adresses IP
    ips = ip_input.split(',')
    ips = [ip.strip() for ip in ips]

    # Vérifier si des adresses IP ont été ajoutées ou supprimées depuis la dernière mise à jour
    for ip in ips:
        if ip not in latency_data:
            latency_data[ip] = deque(maxlen=50)

    # Mettre à jour la latence pour chaque adresse IP
    for ip in ips:
        latency = ping3.ping(ip)
        print("IP valeur", ip, " ", latency)
        if latency is None:
            latency_data[ip].append(1)
            print("Impossible à ping", ip)
        else:
            latency_data[ip].append(latency*1000)

    # Mettre à jour le graphique avec les nouvelles données de latence
    data = []
    for ip in ips:
        # AXE X (BAS)
        x_data = [time.strftime('%d/%m %H:%M:%S', time.localtime(time.time() + intervalps*i)) for i in range(len(latency_data[ip]))]

        # AXE Y (HAUT)
        y_data = [round(j, 2) for j in latency_data[ip]]
        data.append(go.Scatter(x=x_data, y=y_data, mode='lines', name=ip))

    figure = {'data': data, 'layout': go.Layout(xaxis=dict(title='Date & Heure'), yaxis=dict(title='Latence (ms)'))}

    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
