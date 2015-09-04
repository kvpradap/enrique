import ast



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
            assert d.has_key(target) is False, "Variable " + target + " is reused"
            d[target] = node
    return d


def get_target_var(node):
    return node.targets[0].id

def get_input_var(node):
    input = []
    for n in ast.walk(node.value):
        if isinstance(n, ast.Name):
            input.append(n.id)
    return input

def get_mx_mn_lines(n):
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

def get_workflow(hist, var):

    command_node_dict = dict()
    var_node_dict = dict()

    parsed = ast.parse(hist)
    hist_lines = hist.splitlines()

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
            if assign_node_dict.has_key(p) is False:
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
            if assign_node_dict.has_key(n) is False:
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








