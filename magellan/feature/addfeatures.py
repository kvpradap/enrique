def get_feature_function(str, sim, tok):
    d = {}
    fn = 'def fn(ltuple, rtuple):\n'
    fn += '    '
    fn += " return " + str
    exec fn in d
    return d['fn']