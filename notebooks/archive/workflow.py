
# coding: utf-8

# To execute the commands and view the output as shown in this webpage, execute the following command from command prompt
# 
# ipython notebook 
# 
# It should open up a webpage and from there create a new notebook. 
# 
# Note: Page at http://ipython.org/notebook.html provides good introductory information about ipython and its usage.
#     

# In[1]:

# Install autotime ipython module that is useful to time execution of each command
get_ipython().magic(u'install_ext https://raw.github.com/cpcloud/ipython-autotime/master/autotime.py')


# In[2]:

# Load autotime ipython module
get_ipython().magic(u'load_ext autotime')


# In[3]:

import sys


# In[4]:

sys.path.append("c:/Pradap/Research/Python-Packages/enrique/")


# In[5]:

# import magellan into python workspace
import magellan as mg


# In[6]:

A = mg.load_dataset('table_A')


# In[7]:

A.head(10)


# In[8]:

import jpype


# In[9]:

jpype.getDefaultJVMPath()


# In[10]:

# Initialize JVM
mg.init_jvm('C:\\Program Files\\Java\\jre7\\bin\\server\\jvm.dll')


# In[11]:

# import toy datasets
A = mg.load_dataset('table_A')
B = mg.load_dataset('table_B')


# In[12]:

A


# In[13]:

# block using zipcode
ab = mg.AttrEquivalenceBlocker()
C = ab.block_tables(A, B, 'zipcode', 'zipcode', l_output_attrs=['name', 'hourly_wage', 'zipcode'],
                    r_output_attrs=['name', 'hourly_wage', 'zipcode'])


# In[14]:

# dusplay candidate set
C


# In[15]:

# block using hourly_wage
E = ab.block_tables(A, B, 'hourly_wage', 'hourly_wage', l_output_attrs=['birth_year'], r_output_attrs=['birth_year'])


# In[16]:

# display candidate set
E


# In[17]:

# block candidate set C using birth_year
D = ab.block_candset(C, 'birth_year', 'birth_year')


# In[18]:

# display D
D


# In[19]:

# combine blocking outputs C and D. (Note: This is just for illustration, as the output will be just C)
F = mg.combine_block_outputs_via_union([C, D])


# In[20]:

# display F
F


# In[21]:

# sample candidate set F
S = mg.sample_table(F, 13)


# In[22]:

# label candidate set and name the label column as gold_label
L = mg.label_table(S, 'gold_label')


# In[ ]:




# In[24]:

# get features automatically (internally it computes types, attr_corres, sim functions, tokenizers )
feat_table = mg.get_features_for_blocking(A, B)


# In[25]:

# display feature table
feat_table


# In[26]:

# see what tokenizers were used to generate features
mg._current_tokenizers


# In[27]:

# see what simfunctions were used to generate features
mg._current_sim_funs


# In[28]:

# create a new features that computes jaccard measure over address attribute
r = mg.get_feature_fn("jaccard(qgm_3(ltuple['address']), qgm_3(rtuple['address']))",  mg._current_tokenizers, mg._current_sim_funs)


# In[29]:

# see the output from get_feature_fn 
r 


# In[30]:

# add the feature to feature table
mg.add_feature(feat_table, 'add_add_jac_qgm_3_qgm_3', r)


# In[31]:

# check to see whether the feature is indeed added to feature table
feat_table


# In[32]:

# Try executing the newly added function over tuples from A and B
feat_table.ix[6, 'function'](A.ix[2], B.ix[3])


# In[33]:

# Extract feature vectors for labeled candidate set. Also, we mention 'ltable.name, rtable.name' must be included before
# feature vectors and 'gold_label' after the feature vector
s_prime = mg.extract_feat_vecs(L, attrs_before=['ltable.name', 'rtable.name'], feature_table=feat_table, attrs_after=['gold_label'])


# In[34]:

# display feature vector table
s_prime


# In[35]:

# Fitting/Predicting
# Create a set of matchers
nb = mg.NBMatcher() # naive bayes 
dt = mg.DTMatcher() # decision tree
rf = mg.RFMatcher() # random forest


# In[36]:

# Select a matcher using cross validation
m = mg.select_matcher([nb, dt, rf], x=s_prime[list(feat_table['feature_name'])], y=s_prime['gold_label'], k=5 )


# In[37]:

# see what was selected and the stats
m


# In[38]:

# instead of a single matcher, we can choose ensemble of matchers
mc, stats = mg.selector_matcher_combiner([nb, dt, rf], ['majority'], x=s_prime[list(feat_table['feature_name'])], y=s_prime['gold_label'], k=5)


# In[39]:

# see what matcher (or ensemble) was selected
mc


# In[40]:

# train using selected matcher. 
mc.fit(x=s_prime[list(feat_table['feature_name'])], y=s_prime['gold_label'])


# In[41]:

# we want to predict matches from combined candidate set for that we need to generate feature vectors
# NOTE: This is just for illustration, ideally we should remove the rows that was sampled and labeled from combined 
# candidate set F.
c_prime = mg.extract_feat_vecs(F, attrs_before=['ltable.name', 'rtable.name'], feature_table=feat_table)


# In[42]:

# predict the outputs
mc.predict(x=s_prime[list(feat_table['feature_name'])])


# In[43]:

A['ppp'] = 10


# In[45]:

type(A)


# In[3]:

k = None
k > 0.5


# In[8]:

import numpy as np
import pandas as pd


# In[20]:

a = np.array([[10, None, 10], [10, 20, 10], [10, 30, 10]])


# In[21]:

a


# In[22]:

from sklearn.preprocessing import Imputer


# In[23]:

imp = Imputer(missing_values='NaN', strategy='median', axis=0)


# In[24]:

imp.fit(a)


# In[25]:

b = imp.transform(a)


# In[ ]:




# In[26]:

b

