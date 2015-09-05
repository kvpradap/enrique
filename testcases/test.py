# from pyparsing import Word, alphas, alphanums, Literal
# import magellan as mg
# attr_name = Word(alphanums +"_" + "." + "[" +"]" +'"')
# tok_fn = Word(alphanums+"_") + "(" + attr_name + ")"
# wo_tok = Word(alphanums) + "(" + attr_name + "," + attr_name + ")"
# wi_tok = Word(alphanums) + "(" + tok_fn + "," + tok_fn + ")"
# feat = wi_tok | wo_tok
# #t = feat.parseString('jaccard(qgm_3(ltuple.name), qgm_2(rtuple.name))')
# t = feat.parseString('jaccard(qgm_3(ltuple.name]), qgm_2(rtuple.name))')
# sim = mg.get_sim_funs()
# tok = mg.get_single_arg_tokenizers()
# print sim.keys()
# print tok.keys()
# tk = [ t not in tok for t in tok.keys()]
# print tk

import magellan as mg

# A = mg.read_csv('../magellan/datasets/table_A.csv', key = 'ID')
# B = mg.read_csv('../magellan/datasets/table_B.csv', key = 'ID')
# feat_table = mg.get_features_for_blocking(A, B)
#
# # r = mg.get_feature_fn("jaccard(qgm_3(ltuple['address']), qgm_3(rtuple['address']))", mg._current_sim_funs,
# #                       mg._current_tokenizers)
# # print r
# mg.init_jvm()
# print feat_table['feature_name']
# rb = mg.RuleBasedBlocker()
#
# rb.add_rule(['birth_year_birth_year_exm(ltuple, rtuple) == 1'],
#             feat_table
#             )
# #rb.add_rule('birth_year_birth_year_rdf(ltuple, rtuple) > 0.95', feat_table)
# C = rb.block_tables(A, B, l_output_attrs=['name', 'hourly_wage', 'zipcode'],
#                           r_output_attrs=['name', 'hourly_wage', 'zipcode'])
#
# rb = mg.RuleBasedBlocker()
# rb.add_rule(['zipcode_zipcode_exm(ltuple, rtuple) == 1'], feat_table)
# D = rb.block_candset(C)

#print D
# A = mg.load_dataset('table_A')
# B = mg.load_dataset('table_B')
# feat_table = mg.get_features_for_blocking(A, B)

# print A.head()

# import networkx as nx
# import matplotlib.pyplot as plt
#
# def draw_graph(graph, labels=None, graph_layout='shell',
#                node_size=1600, node_color='blue', node_alpha=0.3,
#                node_text_size=12,
#                edge_color='blue', edge_alpha=0.3, edge_tickness=1,
#                edge_text_pos=0.3,
#                text_font='sans-serif'):
#
#     # create networkx graph
#     G=nx.Graph()
#
#     # add edges
#     for edge in graph:
#         G.add_edge(edge[0], edge[1])
#
#     # these are different layouts for the network you may try
#     # shell seems to work best
#     if graph_layout == 'spring':
#         graph_pos=nx.spring_layout(G)
#     elif graph_layout == 'spectral':
#         graph_pos=nx.spectral_layout(G)
#     elif graph_layout == 'random':
#         graph_pos=nx.random_layout(G)
#     else:
#         graph_pos=nx.shell_layout(G)
#
#     # draw graph
#     nx.draw_networkx_nodes(G,graph_pos,node_size=node_size,
#                            alpha=node_alpha, node_color=node_color)
#     nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
#                            alpha=edge_alpha,edge_color=edge_color)
#     nx.draw_networkx_labels(G, graph_pos,font_size=node_text_size,
#                             font_family=text_font)
#
#     if labels is None:
#         labels = range(len(graph))
#
#     edge_labels = dict(zip(graph, labels))
#     nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labels,
#                                  label_pos=edge_text_pos)
#
#     # show graph
#     plt.show()
#
# graph = [(0, 1), (1, 5), (1, 7), (4, 5), (4, 8), (1, 6), (3, 7), (5, 9),
#          (2, 4), (0, 4), (2, 5), (3, 6), (8, 9)]
#
# # you may name your edge labels
# labels = map(chr, range(65, 65+len(graph)))
# #draw_graph(graph, labels)
#
# # if edge labels is not specified, numeric labels (0, 1, 2...) will be used
# draw_graph(graph)


import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pylab

G = nx.DiGraph()

G.add_edges_from([('A', 'B'),('C','D'),('G','D')], weight=1)
G.add_edges_from([('D','A'),('D','E'),('B','D'),('D','E')], weight=2)
G.add_edges_from([('B','C'),('E','F')], weight=3)
G.add_edges_from([('C','F')], weight=4)


val_map = {'A': 1.0,
                   'D': 0.5714285714285714,
                              'H': 0.0}

values = [val_map.get(node, 0.45) for node in G.nodes()]
edge_labels = dict([((u,v,),d['weight'])
                 for u,v,d in G.edges(data=True)])
red_edges = [('C','D'),('D','A')]
edge_colors = ['black' if not edge in red_edges else 'red' for edge in G.edges()]

pos=nx.spring_layout(G)
nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
nx.draw(G,pos, node_color = values, node_size=1500,edge_color=edge_colors,edge_cmap=plt.cm.Reds)
pylab.show()