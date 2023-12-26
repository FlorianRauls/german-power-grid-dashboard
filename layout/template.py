import plotly.graph_objects as go


# just a template to use for all the other layouts in the project
my_ibcs_template = dict(
    layout = go.Layout(title_font=dict(size=20, color='#000000', family='Roboto'),
                          font=dict(size=14, color='#000000', family='Roboto'),
                          plot_bgcolor='#FFFFFF',
                          paper_bgcolor='#FFFFFF',
                          xaxis=dict(showgrid=True, showticklabels=True),
                          yaxis=dict(showgrid=False, zeroline=True, showticklabels=False, zerolinecolor='#000000'),
                          scene=dict(xaxis=dict(showgrid=False, zeroline=True, showticklabels=True)),
                          colorway= ['#333333', '#555555', '#999999', '#777777'],
                          margin=dict(l=100, r=100, t=100, b=100),
                          hovermode='closest',
                          showlegend=False,
                          title='Plot Title',
                          
                )
)   


# add styling for titles
titles_styles = {
    'color': '#000000',
    'fontFamily': 'Roboto',
    'fontSize': 24,
    'paddingTop': '1px',
    'paddingBottom': '1px',
    'marginBottom': '1px',
    'marginTop': '1px',
}