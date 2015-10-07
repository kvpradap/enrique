class command_node(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.input_vars = []
        self.output_vars = None

class var_node(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.output_by = None
        self.used_by=[]


def get_assign_nodes(parsed):
    import ast
    d = dict()
    for node in ast.walk(parsed):
        if isinstance(node, ast.Assign):
            assert len(node.targets) is 1, "Currently handle a single output"
            target = node.targets[0].id
            input = []
            for n in ast.walk(node.value):
                if isinstance(n, ast.Name):
                    input.append(n.id)
            assert target not in input, "Same variable is in both input and output list"
            assert d.has_key(target) == False, "Variable " + target + " is reused"
            d[target] = node
    return d


def get_target_var(node):
    return node.targets[0].id

def get_input_var(node):
    import ast
    input = []
    for n in ast.walk(node.value):
        if isinstance(n, ast.Name):
            input.append(n.id)
    return input

def get_mx_mn_lines(n):
    import ast
    mn = 10e6
    mx = 0
    for node in ast.walk(n):
        if hasattr(node, "__dict__"):
            if node.__dict__.has_key('lineno'):
                ln = node.__dict__['lineno']
                if mn > ln:
                    mn = ln
                if ln > mx:
                    mx = ln
    return mn, mx

def get_workflow(hst, var):
    import ast
    command_node_dict = dict()
    var_node_dict = dict()

    parsed = ast.parse(hst)
    hist_lines = hst.splitlines()

    assign_node_dict = get_assign_nodes(parsed)
    assign_node_visit = dict(zip(assign_node_dict.keys(), [0]*len(assign_node_dict.keys())))
    command_count = 1
    inp_list = [var]
    while len(inp_list) > 0:
        var = inp_list.pop()
        assign_node_visit[var] = 1
        node = assign_node_dict.get(var, None)
        if node is None:
            raise KeyError('Key %s not present' %var)

        out = get_target_var(node)
        inp = get_input_var(node)
        inp = [a for a in inp if assign_node_dict.has_key(a)]
        for p in inp:
            if assign_node_dict.has_key(p) == False:
                print "WARN %s is not there in assign nodes" %n
                continue
            if assign_node_visit[p] is 0:
                inp_list.append(p)

        cmd_id = 'C'+str(command_count)
        mn, mx = get_mx_mn_lines(node)
        if mn != mx:
            t = [mn-1, mx-1]
        else:
            t = [mn-1]
        cmd_name = ' '.join([hist_lines[x] for x in t])
        cmd_node = command_node(cmd_id, cmd_name)
        command_count +=1
        cmd_node.input_vars=inp
        cmd_node.output_vars=[out]
        command_node_dict[cmd_id] = cmd_node

        if var_node_dict.has_key(out):
            v = var_node_dict.get(out)
            if v.output_by is not None:
                print v.output_by
                print v.used_by
                raise AssertionError('The variable seems to be reused')
            v.output_by = cmd_id
            var_node_dict[out] = v
        else:
            v = var_node(out, out)
            v.output_by = cmd_id
            var_node_dict[out] = v


        for n in inp:
            if assign_node_dict.has_key(n) == False:
                print "%s is not there in assign nodes" %n
                continue
            if var_node_dict.has_key(n) is True:
                v = var_node_dict[n]
                v.used_by.append(cmd_id)
                var_node_dict[n] = v
            else:
                v = var_node(n, n)
                v.used_by.append(cmd_id)
                var_node_dict[n] = v
    return command_node_dict, var_node_dict

def draw_graph():
    import networkx as nx
    import matplotlib.pyplot as plt
    G = nx.DiGraph()

    G.add_edges_from([('A', 'B'),('C','D'),('G','D')], weight=1)
    G.add_edges_from([('D','A'),('D','E'),('B','D'),('D','E')], weight=2)
    G.add_edges_from([('B','C'),('E','F')], weight=3)
    G.add_edges_from([('C','F')], weight=4)


    val_map = {'A': 1.0,
                       'D': 0.5714285714285714,
                                  'H': 0.0}

    values = [val_map.get(node, 0.45) for node in G.nodes()]
    edge_labels=dict([((u,v,),d['weight'])
                     for u,v,d in G.edges(data=True)])
    red_edges = [('C','D'),('D','A')]
    edge_colors = ['black' if not edge in red_edges else 'red' for edge in G.edges()]

    pos=nx.circular_layout(G)
    nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
    nx.draw(G,pos, node_color = values, node_size=1500,edge_color=edge_colors,edge_cmap=plt.cm.Reds, with_labels=True)

def get_sources(cmd_dict):
    sources = []
    for key, value in cmd_dict.iteritems():
        if len(value.input_vars) == 0:
            sources.append(value)
    return sources

def get_edge_list(cmd_dict, var_dict):
    nodes = get_sources(cmd_dict)
    edge_list=[]
    while len(nodes) != 0:
        node = nodes.pop()
        if isinstance(node, command_node):
            for v in node.output_vars:
                vnode = var_dict[v]
                if (node.id, vnode.id) not in edge_list:
                    edge_list.append((node.id, vnode.id))
                    nodes.append(vnode)
        if isinstance(node, var_node):
            for v in node.used_by:
                cnode = cmd_dict[v]
                if (node.id, cnode.id) not in edge_list:
                    edge_list.append((node.id, cnode.id))
                    nodes.append(cnode)
    return edge_list




def draw_workflow(h, var):
    c, v = get_workflow(h, var)
    ed = get_edge_list(c, v)

    for k, v in c.iteritems():
        print k + " : " + v.name
        print "\n"


    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()
    G.add_edges_from(ed)
    val_map = dict(zip(c.keys(), [0.4]*6))
    values = [val_map.get(node, 0.5) for node in G.nodes()]
    pos=nx.circular_layout(G, scale =8)
    #nx.draw_networkx_edge_labels(G,pos,edge_labels=None)
    nx.draw(G,pos, node_color=values, node_size=1500, with_labels=True, cmap=plt.get_cmap('Pastel1'))

