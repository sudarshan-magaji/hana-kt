from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

data=pd.read_excel('Extract2.xlsx')
cvs=data.groupby(['OBJECT_NAME'])
cv_claim=cvs.get_group('CV_CLAIM')
cv_claim['SOURCE_NODE']=cv_claim['SOURCE_NODE'].fillna('')
cv_claim['SOURCE_NODE']=cv_claim['SOURCE_NODE'].replace('#','',regex=True)
cv_claim['TARGET_NODE']=cv_claim['TARGET_NODE'].fillna('')
edges=list(cv_claim.groupby(['SOURCE_NODE','TARGET_NODE']).groups.keys())[2:]
nodes=list(pd.concat([cv_claim['SOURCE_NODE'],cv_claim['TARGET_NODE']]).unique())
nodes.remove('')

def get_nodes_dict(nodes):
    output=[]
    for node in nodes:
        output.append({'data':{'id':node,'label':node}})
    return output

def get_edges_dict(edges):
    output=[]
    for edge in edges:
        output.append({'data':{'source':edge[0],'target':edge[1]}})
    return output

final_nodes=get_nodes_dict(nodes)
final_edges=get_edges_dict(edges)
output_elements=final_nodes+final_edges

def get_fields_list(node_name):
    return list(cv_claim[['TARGET_NODE','TARGET_VALUE']].groupby('TARGET_NODE').get_group(node_name)['TARGET_VALUE'])

card = dbc.Card(
    dbc.ListGroup(id='fields_list',
        flush=True,
    ),
    style={'position':'fixed','top':0,'right':0,"width": "15rem"},
)

app.layout = html.Div([dbc.Col([
    cyto.Cytoscape(
        id='cyto',
        layout={'name': 'breadthfirst',
        		'roots': '[id = "logicalModel"]'},
        style={'width': '80%', 'height': '630px'},
        elements=output_elements
    ),
    card])
])

@app.callback(
    Output('fields_list', 'children'),
    Input('cyto', 'tapNodeData'))
def populate_fields(node):
    return [dbc.ListGroupItem(field) for field in get_fields_list(node['label'])]

if __name__ == '__main__':
    app.run_server(debug=True)