
import sys
sys.path.append('/Users/pradap/Documents/Research/Python-Package/enrique/')
import magellan as mg
import pandas as pd
mg.init_jvm()
wal =  mg.read_csv(mg.get_install_path() + '/datasets/books/walmart.csv',
                    dtype={'isbn':pd.np.str, 'pages':pd.np.str, 'volume':pd.np.str, 'editionNum':pd.np.str},  
                    low_memory=False, key='id')

bwk = mg.read_csv(mg.get_install_path() + '/datasets/books/bowker.csv', 
                  dtype={'isbn':pd.np.str, 'pages':pd.np.str, 'volume':pd.np.str, 'editionNum':pd.np.str},  
                  low_memory=False, key='id')

ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(wal, bwk, 'isbn', 'isbn', ['title', 'author'], ['title', 'author'])


L = mg.read_csv('label_ab_correct_books.csv', ltable=wal, rtable=bwk)

feat_table = mg.get_features_for_matching(wal, bwk)


f = feat_table.ix[[3,7,18,26, 53]]

G = mg.extract_feat_vecs(L, feat_table=f, attrs_after='gold')

dt = mg.DTMatcher()
svm = mg.SVMMatcher()
rf = mg.RFMatcher()
nb = mg.NBMatcher()
lg = mg.LogRegMatcher()


# impute values
G.fillna(0, inplace=True)


selected, stats = mg.select_matcher([dt, rf, svm, nb, lg], table=G, exclude_attrs=['_id', 'ltable.id', 'rtable.id', 'gold'],
                                    target_attr='gold', metric='precision')
d = mg.train_test_split(G, train_proportion=0.7)
# train = d['train']
# test = d['test']
# train.to_csv('train.csv')
# test.to_csv('test.csv')
train = mg.read_csv('train.csv', ltable=wal, rtable=bwk)
test = mg.read_csv('test.csv', ltable=wal, rtable=bwk)

dt.fit(table=train, exclude_attrs=['_id', 'ltable.id', 'rtable.id', 'gold'], target_attr='gold')
# ret_val, node_list = mg.vis_tuple_debug_dt_matcher(dt, G.iloc[[0]], exclude_attrs=['_id', 'ltable.id', 'rtable.id', 'gold'])
# print ret_val
# print node_list
mg.vis_debug_dt(dt, train, test, exclude_attrs=['_id', 'ltable.id', 'rtable.id', 'gold'], target_attr='gold')
print 'Hi'