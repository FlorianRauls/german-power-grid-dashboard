import plotly.graph_objects as go


# just a template to use for all the other layouts in the project
my_ibcs_template = dict(
    layout = go.Layout(title_font=dict(size=24, color='#000000', family='Roboto'),
                          font=dict(size=18, color='#000000', family='Roboto'),
                          plot_bgcolor='#FFFFFF',
                          paper_bgcolor='#FFFFFF',
                          xaxis=dict(showgrid=False, zeroline=True, showticklabels=True, linecolor='#000000', linewidth=1, mirror=True),
                          yaxis=dict(showgrid=False, zeroline=False, showticklabels=True),
                          scene=dict(xaxis=dict(showgrid=False, zeroline=True, showticklabels=True)),
                          colorway= ['#999999', '#777777', '#555555', '#333333', '#111111'],
                          margin=dict(l=100, r=100, t=100, b=100),
                          hovermode='closest',
                          showlegend=False,
                          title='Plot Title',
                          
                          updatemenus=[dict(type='buttons',
                                          showactive=False,
                                          y=1,
                                          x=1.3,
                                          xanchor='right',
                                          yanchor='top',
                                          pad=dict(t=0, r=10),
                                          buttons=[dict(label='Play',
                                                         method='animate',
                                                         args=[None, dict(frame=dict(duration=50, redraw=True),
                                                                            transition=dict(duration=0),
                                                                            fromcurrent=True,
                                                                            mode='immediate')])])]),
                          
)
