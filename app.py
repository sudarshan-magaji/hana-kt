from dash import Dash, html, dcc, Input, Output, ALL
import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
from dash.exceptions import PreventUpdate

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

data=pd.read_excel('Extract2.xlsx')
cvs=data.groupby(['OBJECT_NAME'])
cv_claim=cvs.get_group('CV_CLAIM')
#cv_claim['SOURCE_NODE']=cv_claim['SOURCE_NODE'].fillna('')
cv_claim['SOURCE_NODE']=cv_claim['SOURCE_NODE'].replace('#','',regex=True)
#cv_claim['TARGET_NODE']=cv_claim['TARGET_NODE'].fillna('')
#cv_claim=cv_claim[~cv_claim['TARGET_VALUE'].astype(str).str.contains('JOIN\$',regex=True)]
edges=list(cv_claim[['TARGET_NODE','SOURCE_NODE']].drop_duplicates(['TARGET_NODE','SOURCE_NODE']).dropna().apply(lambda x: (x['TARGET_NODE'],x['SOURCE_NODE']),axis=1))
nodes=cv_claim[['TARGET_NODE','SOURCE_NODE']].drop_duplicates(['TARGET_NODE','SOURCE_NODE']).dropna().stack().unique()

target=(cv_claim['TARGET_NODE']+'+'+cv_claim['TARGET_VALUE'])
source=(cv_claim['SOURCE_NODE']+'+'+cv_claim['SOURCE_VALUE'])
df=pd.DataFrame([source,target]).T
df.columns=['source','target']
df=df.dropna()
target=list(df['target'])
source=list(df['source'])
mapping={target[i]:source[i] for i in range(len(target))}

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

def find_lineage(target):
    path=[target]
    while(target in mapping.keys()):
        path.append(mapping[target])
        target=mapping[target]
    return path

final_nodes=get_nodes_dict(nodes)
final_edges=get_edges_dict(edges)
output_elements=final_nodes+final_edges

def get_fields_list(node_name):
    return list(cv_claim[['TARGET_NODE','TARGET_VALUE']].groupby('TARGET_NODE').get_group(node_name)['TARGET_VALUE'])



CYTO_STYLESHEET=[{'selector':'node','style':{'padding':'30px','content':'data(label)','text-valign': 'center','text-halign': 'center','height':'20px','width':'label','shape':'cut-rectangle','font-size':'30px','text-wrap':'wrap'},},

                     {'selector':'edge','style':{'curve-style':'taxi','width':'3px','arrow-shape':'vee'}}]


card = dbc.Card(
    dcc.Dropdown(id='fields_list',placeholder='Select a node'
    ),
    style={'position':'fixed','top':0,'right':0,"width": "15rem"},
)

app.layout = html.Div([dbc.Col([
    cyto.Cytoscape(
        id='cyto',
        layout={'name': 'breadthfirst',
        		'roots': '[id = "logicalModel"]','grid':'true','spacingFactor':1},
        style={'width': '80%', 'height': '630px'},
        stylesheet=CYTO_STYLESHEET,
        elements=output_elements
    ),
    card])
])

@app.callback(
    Output('fields_list', 'options'),
    Input('cyto', 'tapNodeData'),prevent_initial_call=True)
def populate_fields(node):
    print(node['label'])
    try:
        fields=get_fields_list(node['label'])
        return [{'label':field,'value':node['label']+'+'+field} for field in fields]
    except KeyError:
        return []

@app.callback(
    Output('cyto', 'stylesheet'),
    Input('fields_list', 'value'),prevent_initial_call=True)
def highlight_path(value):
    path=find_lineage(value)
    path=[i.split('+')[0] for i in path]
    node_selector=', '.join(["[id='{}']".format(i) for i in path])
    stylesheet=CYTO_STYLESHEET[:]
    stylesheet.append({'selector':node_selector,'style':{'background-color':'#F0E614'}})
    return stylesheet


if __name__ == '__main__':
    app.run_server(debug=True)