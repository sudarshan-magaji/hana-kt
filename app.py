from dash import Dash, html, dcc
import dash_cytoscape as cyto
import pandas as pd

app = Dash(__name__)

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

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-two-nodes',
        layout={'name': 'breadthfirst',
        		'roots': '[id = "logicalModel"]'},
        style={'width': '100%', 'height': '630px'},
        elements=output_elements
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)