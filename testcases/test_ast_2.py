import ast
from collections import OrderedDict

# declare command and variable nodes
class command_node(object):
    def __init__(self, id, line_no, command_string):
        self.id = id
        self.command_string = command_string
        self.line_no = line_no
        self.input_vars = []
        self.output_vars = None

class variable_node(object):
    def __init__(self, id, line_no, variable_name, command_string=None):
        self.id = id
        self.line_no = line_no
        self.variable_name = variable_name
        if command_string is not None:
            self.command_string = command_string
        # output by which commands
        self.output_by = None
        # used by which commands
        self.used_by = []
# ---------------------------------------------------

def get_all_assign_nodes(parsed):
    d = OrderedDict()
    for node in ast.walk(parsed):
        if isinstance(node, ast.Assign):
            assert len(node.targets) is 1, 'Only single outputs are handled'
            lno = node.lineno
            out = node.targets[0].id
            inp = []
            for n in ast.walk(node.value):
                if isinstance(n, ast.Name):
                    inp.append(n.id)
            assert out not in inp, 'Same variable is in both input and output list'
            d[(lno, out)] = node
    return d

def get_assign_nodes_from_var(assign_dict, var):
    keys = assign_dict.keys()
    var_keys = [x for x in keys if x[1] == var]
    assert  len(var_keys) != 0, 'Given variable is not part of assign nodes'
    var_keys.sort(key=lambda  tup:tup[0], reverse=True)
    var_index = keys.index[var_keys[0]]
    d = OrderedDict()
    for i in range(0, var_index+1):
        d[keys[i]] = assign_dict[keys[i]]
    return d


def get_assign_node_for_var(assign_dict, var, line_no):
    keys = assign_dict.keys()
    var_keys = [x for x in keys if x[1] == var]
    assert len(var_keys) != 0, 'Given variable is not part of assign nodes'
    var_keys.sort(key=lambda  tup:tup[0], reverse=True)
    k = var_keys[0]
    return assign_dict[k]

