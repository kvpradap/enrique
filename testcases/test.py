import magellan as mg

A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')

mg.init_jvm('/Library/Java/JavaVirtualMachines/jdk1.8.0_45.jdk/Contents/Home/jre/lib/server/libjvm.dylib')
from magellan.feature.simfunctions import *
from magellan.feature.tokenizers import *
def block_fn_1(ltuple, rtuple):
    val = jaccard(tok_qgram(ltuple['address'], 3), tok_qgram(rtuple['address'], 3))
    if  val < 0.4:
        return True
    else:
        return False

def block_fn_2(x, y):
    val = lev(x['name'], y['name'])
    if val < 0.5:
        return True
    else:
        return False

bb = mg.BlackBoxBlocker()
bb.set_black_box_function(block_fn_1)
C = bb.block_tables(A, B, l_output_attrs='name', r_output_attrs='name')
print C
bb.set_black_box_function(block_fn_2)
D = bb.block_candset(C)
print D

