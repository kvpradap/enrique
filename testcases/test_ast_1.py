
class command_node(object):
    def __init__(self, id, line_no, command_string):
        self.id = id
        self.command_string = command_string
        self.line_no = line_no
        self.input_vars = []
        self.output_vars = None

class variable_node(object):
    def __init__(self, id, line_no, name, command_string):
        self.id = id
        self.name = name
        self.line_no = line_no
        self.output_by = None
        self.used_by = []
        self.command_string = command_string # this information is redundant


import ast
from collections import OrderedDict
def get_assign_nodes(parsed):
    d = OrderedDict()
    for node in ast.walk(parsed):
        if isinstance(node, ast.Assign):
            assert len(node.targets) is 1, "Multiple outputs are not handled"
            lno = node.lineno
            target = node.targets[0].id
            input = []
            for n in ast.walk(node.value):
                if isinstance(n, ast.Name):
                    input.append(n.id)
            assert target not in input, "Same variable is in both input and output list"
            d[(lno, target)] = node
    return d

def get_target_var(node):
    return node.targets[0].id

def get_input_var(node):
    input = []
    for n in ast.walk(node.value):
        if isinstance(n, ast.Name):
            input.append(n.id)
    return input


def check_dag(assign_dict, var):
    keys = assign_dict.keys()
    var_keys = [x for x in keys if x[1] == var]
    assert len(var_keys) != 0, "Given variable is not part of assign nodes"
    var_keys.sort(key=lambda tup:tup[0], reverse=True)
    var_index = keys.index(var_keys[0])
    edge_list = []
    node_names = list(set([x[1] for x in keys]))
    for i in range(0, var_index+1):
        node = assign_dict[keys[i]]
        out = get_target_var(node)
        inp = get_input_var(node)
        # create edges
        for p in inp:
            if p in node_names:
                edge_list.append((p, out)) # the order is imp
    edge_list =  list(set(edge_list))
    ret_val = check_dag_edg(edge_list)
    return ret_val

def get_src_from_edge_list(edge_list):
    f_nodes = set([x[0] for x in edge_list])
    t_nodes = set([x[1] for x in edge_list])
    return list(f_nodes - t_nodes)

def remove_edges(edge_list, source):
    e = [x for x in edge_list if x[0] == source]
    return list(set(edge_list) - set(e))

def check_dag_edg(edge_list):
    e = edge_list
    s = get_src_from_edge_list(edge_list)

    while len(s) > 0:
        for n in s :
            e = remove_edges(e, n)
        s = get_src_from_edge_list(e)
    assert len(e) == 0, "The workflow cotains a cycle"
    return True

def get_assign_nodes_v(assign_dict, var):
    keys = assign_dict.keys()
    var_keys = [x for x in keys if x[1] == var]
    assert len(var_keys) != 0, "Given variable is not part of assign nodes"
    var_keys.sort(key=lambda tup:tup[0], reverse=True)
    var_index = keys.index(var_keys[0])
    d = dict()
    for idx in range(0, var_index + 1):
        k = keys[idx]
        pass


    pass

def get_workflow(h, v):
    command_node_dict = dict()
    var_node_dict = dict()
    parsed = ast.parse(h)
    hist_lines = h.splitlines()

    assign_node_dict = get_assign_nodes(parsed)
    assign_node_v_dict = get_assign_nodes_v(assign_node_dict, v)


    pass

histo="""
A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')
ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(A, B, 'zipcode', 'zipcode', l_output_attrs=['name', 'hourly_wage', 'zipcode'],
                    r_output_attrs=['name', 'hourly_wage', 'zipcode'])
S = mg.sample_one_table(C, 13)
C = mg.label(S, 'gold_label')
"""
parsed = ast.parse(histo)
assign_node_dict = get_assign_nodes(parsed)

t = check_dag(assign_node_dict, 'S')


print t











