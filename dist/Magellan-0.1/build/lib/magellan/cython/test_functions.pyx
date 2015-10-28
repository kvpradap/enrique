import cython
def compute_jaccard_index(set_1, set_2):
    n = len(set_1.intersection(set_2))
    d = float(len(set_1) + len(set_2) - n)
    if d == 0:
        return 0
    return n / d

def ngrams(input, n):
  output = []
  input = list(input)
  for i in range(len(input)-n+1):
    g = ''.join(input[i:i+n])
    output.append(g)
  return output