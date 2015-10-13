#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import heapq as hq
import numpy
import functools

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

import magellan as mg
from magellan.core.mtable import MTable

from collections import namedtuple
from collections import defaultdict
from operator import attrgetter

def debug_blocker(ltable, rtable, candidate_set, pred_list_size=200, field_corres_list=None):
	"""
	Debug the blocker. The basic idea is trying to suggest the user a list of record pairs
	out of the candidate set with high (document) jaccard similarity. The object of similarity
	measurement (document) is generated based on a string concatenation method with field
	selection. Given the suggestion list, the user should go through the pairs and determine if
	there are, and how many true matches in it. And based on this information, the user can
	determine if further improvement on the blocking step is necessary (Ex. if there are many
	true matches in the list, the user may conclude that the blocking step is flawed, and should
	revise it to produce a better candidate set).

	Parameters
	----------
	ltable, rtable : MTable
		Input MTables
	candidate_set : MTable
		The candidate set table after performing blocking on ltable and rtable
	pred_list_size : int
		The size of the output suggestion list
	field_corres_list : list (of tuples), defaults to None
		The list of field pairs from ltable and rtable. Each pair indicates a field correspondence
		between two tables. Since ltable and rtable can have different schemas, it' necessary to
		have this parameter to build the field correspondence to make sure the string concatenation
		algorithm runs correctly.
		Note each pair in the list should be represented as a tuple in the following format:
							(some_ltable_field, some_rtable_field)

	Returns
	-------
	suggestion_table : MTable
		Contains a list of pair suggestions with high jaccard similarity. The output MTable contains
		the following fields:
			* _id
			* similarity (of the record pair)
			* ltable record key value
			* rtable record key value
			* field pairs from filtered corres_list (removing the numeric types)
				ltable_field_1
				rtable_field_1 (corresponding to ltable_field_1)
				ltable_field_2
				rtable_field_2 (corresponding to ltable_field_2)
					  .
					  .
				ltable_field_k
				rtable_field_k (corresponding to ltable_field_k)
	"""

	# Basic checks.
	if len(ltable) == 0:
		raise StandardError('Error: ltable is empty!')
	if len(rtable) == 0:
		raise StandardError('Error: rtable is empty!')
	if pred_list_size <= 0:
		raise StandardError('The input parameter: \'pred_list_size\' is less than or equal to 0. Nothing needs to be done!')

	logging.info('\nPreparing for debugging blocker')

	# Check the user input field correst list (if exists) and get the raw version of
	# our internal correst list.
	check_input_field_correspondence_list(ltable, rtable, field_corres_list)
	corres_list = get_field_correspondence_list(ltable, rtable, field_corres_list)

	# Build the (col_name: col_index) dict to speed up locating a field in the schema.
	ltable_col_dict = build_col_name_index_dict(ltable)
	rtable_col_dict = build_col_name_index_dict(rtable)

	# Filter correspondence list to remove numeric types. We only consider string types
	# for document concatenation.
	filter_corres_list(ltable, rtable, ltable_col_dict, rtable_col_dict, corres_list)
	#logging.info('\nFiltered field correspondence list:\n' + str(corres_list))

	# Get field filtered new table.
	ltable_filtered, rtable_filtered = get_filtered_table(ltable, rtable, corres_list)

	# Select features.
	"""TODO(hanli): currently we don't select the key fields even if they have the largest score.
	# This is because the values of the key field could be simply domain-specific serial numbers,
	# which might be meaningless or even harmful (when two tables use different key formats).
	# Modify it if this ituition is not proper."""
	feature_list = select_features(ltable_filtered, rtable_filtered)
	if len(feature_list) == 0:
		raise StandardError('\nError: the selected field list is empty, nothing could be done! ' +
			'Please check if all table fields are numeric types.')
	#logging.info('\nSelected fields for concatenation:\n' + str([(ltable_filtered.columns[i], rtable_filtered.columns[i]) for i in feature_list]))

	# Get each table kgram dict.
	ltable_kgram_dict = get_kgram_dict(ltable_filtered, ltable_filtered.get_key(), feature_list, 3)
	rtable_kgram_dict = get_kgram_dict(rtable_filtered, rtable_filtered.get_key(), feature_list, 3)

	# Build inverted index on ltable kgrams to speed up debugging.
	inverted_index = build_inverted_index(ltable_kgram_dict)

	ltable_key = candidate_set.get_property('foreign_key_ltable')
	rtable_key = candidate_set.get_property('foreign_key_rtable')
	
	indexed_candidate_set = candidate_set.set_index([rtable_key, ltable_key], drop=False)
	candidate_index_key_set = set(indexed_candidate_set[rtable_key])
	#logging.info('\nCandidate set size: %d' %(len(indexed_candidate_set)))

	rtable_len = len(rtable_filtered)
	progress_dict = {}
	for i in range(10):
		progress_dict[int((i + 1) * 1.0 / 10 * rtable_len)] = (i + 1) * 1.0 / 10

	logging.info('\nStart debugging blocker')
	pred_index_list = []
	count = 0
	for rkey in rtable_kgram_dict:
		count += 1
		#if count == 500:
			#print pred_index_list
		#	break
		if rtable_len <= 10:
			logging.info('\nDebugging %s' %('{percent:.2%}'.format(percent=count * 1.0 / rtable_len)))
		else:
			if count in progress_dict:
				logging.info('\nDebugging %s' %('{percent:.2%}'.format(percent=progress_dict[count])))

		rkgram_set = rtable_kgram_dict[rkey]
		if len(rkgram_set) == 0:
			continue
		cand_set = {}
		if rkey in candidate_index_key_set:
			cand_set = indexed_candidate_set.ix[rkey].index.values
		ltable_index_set = get_potential_match_set(rkgram_set, inverted_index)
		for lkey in ltable_index_set:
			if lkey in cand_set:
				continue
			jac_sim = jaccard_kgram_sim(ltable_kgram_dict[lkey], rkgram_set)
			if len(pred_index_list) == pred_list_size:
				hq.heappushpop(pred_index_list, (jac_sim, lkey, rkey))
			else:
				hq.heappush(pred_index_list, (jac_sim, lkey, rkey))

	ret_data_frame = generate_prediction_table(ltable_filtered, rtable_filtered, pred_index_list)

	"""This print is for debugging"""
	#print ret_data_frame

	ret_mtable = MTable(ret_data_frame)
	ret_mtable.set_property('foreign_key_ltable', ltable_key)
	ret_mtable.set_property('foreign_key_rtable', rtable_key)
	ret_mtable.set_property('ltable', ltable)
	ret_mtable.set_property('rtable', rtable)

	logging.info('\nFinish debugging blocker')

	return ret_mtable

def get_filtered_table(ltable, rtable, corres_list):
	ltable_cols = [col_pair[0] for col_pair in corres_list]
	rtable_cols = [col_pair[1] for col_pair in corres_list]
	l_mtable = MTable(ltable[ltable_cols], key=ltable.get_key())
	r_mtable = MTable(rtable[rtable_cols], key=rtable.get_key())
	return l_mtable, r_mtable


def build_col_name_index_dict(table):
	col_dict = {}
	col_names = list(table.columns)
	for i in range(len(col_names)):
		col_dict[col_names[i]] = i
	return col_dict

def filter_corres_list(ltable, rtable, ltable_col_dict, rtable_col_dict, corres_list):
	ltable_dtypes = list(ltable.dtypes)
	ltable_key = ltable.get_key()
	rtable_dtypes = list(rtable.dtypes)
	rtable_key = rtable.get_key()
	for i in reversed(range(len(corres_list))):
		lcol_name = corres_list[i][0]
		rcol_name = corres_list[i][1]
		# Filter the pair where both fields are numeric types.
		if ltable_dtypes[ltable_col_dict[lcol_name]] != numpy.dtype('O') and rtable_dtypes[rtable_col_dict[rcol_name]] != numpy.dtype('O'):
			if lcol_name != ltable_key and rcol_name != rtable_key:
				corres_list.pop(i)

	if len(corres_list) == 0:
		raise StandardError('The field correspondence list is empty after filtering: nothing could be done!')


# If the user provides the fields correspondence list, check if each field is in the corresponding table.
def check_input_field_correspondence_list(ltable, rtable, field_corres_list):
	if field_corres_list is None:
		return
	true_ltable_fields = list(ltable.columns)
	true_rtable_fields = list(rtable.columns)
	given_ltable_fields = [field[0] for field in field_corres_list]
	given_rtable_fields = [field[1] for field in field_corres_list]
	for given_field in given_ltable_fields:
		if given_field not in true_ltable_fields:
			raise StandardError('Error in checking user input field correspondence: the field \'%s\' is not in the ltable!' %(given_field))
	for given_field in given_rtable_fields:
		if given_field not in true_rtable_fields:
			raise StandardError('Error in checking user input field correspondence: the field \'%s\' is not in the rtable!' %(given_field))
	return

def get_field_correspondence_list(ltable, rtable, field_corres_list):
	corres_list = []
	if field_corres_list is None or len(field_corres_list) == 0:
		corres_list = mg.get_attr_corres(ltable, rtable)['corres']
		if len(corres_list) == 0:
			raise StandardError('Error: the field correspondence list is empty. Nothing can be done!')
	else:
		#corres_list = field_corres_list
		for tu in field_corres_list:
			corres_list.append(tu)

	return corres_list

def build_table_key_value_row_index_dict(table, key):
	dic = {}
	values = list(table[key])
	for i in range(len(values)):
		dic[str(values[i])] = i

	return dic

def generate_prediction_table(ltable, rtable, pred_index_list):
	pred_index_list.sort(key=lambda tup: tup[0], reverse = True)
	ret_data_col_name_list = ['similarity']
	ltable_col_names = list(ltable.columns)
	rtable_col_names = list(rtable.columns)

	for i in range(len(ltable_col_names)):
		ret_data_col_name_list.append('ltable.' + ltable_col_names[i])
		ret_data_col_name_list.append('rtable.' + rtable_col_names[i])

	lkey = ltable.get_key()
	rkey = rtable.get_key()
	ltable_dict = build_table_key_value_row_index_dict(ltable, lkey)
	rtable_dict = build_table_key_value_row_index_dict(rtable, rkey)
	ret_tuple_list = []
	for pred_tuple in pred_index_list:
		ret_tuple = [pred_tuple[0]]
		lrecord = list(ltable.ix[ltable_dict[str(pred_tuple[1])]])
		rrecord = list(rtable.ix[rtable_dict[str(pred_tuple[2])]])
		for i in range(len(lrecord)):
			ret_tuple.append(lrecord[i])
			ret_tuple.append(rrecord[i])
		ret_tuple_list.append(ret_tuple)
	data_frame = pd.DataFrame(ret_tuple_list)
	# When the ret data frame is empty, we cannot assign column names.
	if len(data_frame) == 0:
		return data_frame
	
	data_frame.columns = ret_data_col_name_list
	return data_frame

def jaccard_kgram_sim(lkgram_set, rkgram_set):
	#total = len(lset)
	#if total == 0 and len(rset) == 0:
	#	return 0.0;
	#common = 0;
	#for kgram in rset:
	#	if kgram in lset:
	#		common += 1;
	#	else:
	#		total += 1;
	#return common * 1.0 / total

	union_size = len(lkgram_set | rkgram_set)
	jac_sim = 0.0
	if union_size > 0:
		jac_sim = len(lkgram_set & rkgram_set) * 1.0 / union_size
	return jac_sim

def replace_nan_to_empty(field):
	if pd.isnull(field):
		return ''
	elif type(field) in [float, numpy.float64, int, numpy.int64]:
		return str('{0:.0f}'.format(field))
	else:
		return str(field)

def get_kgram(record, feature_list, k):
	str_list = [replace_nan_to_empty(field) for field in record[feature_list]]
	record_str = ' '.join(str_list).lower()
	kgram_set = set()
	for i in range(len(record_str) - k + 1):
		kgram_set.add(record_str[i : i + k])
	return kgram_set

def get_kgram_dict(table, key, feature_list, k):
	kgram_dict = {}
	for i in range(len(table)):
		#if i > 0 and i % 5000 == 0:
		#	print 'generating table kgram set:', i
		record = table.ix[i]
		kgram_dict[record[key]] = get_kgram(record, feature_list, k)

	return kgram_dict

def get_feature_weight(table):
	num_records = len(table)
	if num_records == 0:
		raise StandardError('Error: empty table!')
	weight = []
	for col in table.columns:
		value_set = set()
		non_empty_count = 0;
		col_values = table[col]
		for value in col_values:
			if not pd.isnull(value):
				value_set.add(value)
				non_empty_count += 1
		selectivity = 0.0
		if non_empty_count != 0:
			selectivity = len(value_set) * 1.0 / non_empty_count
		non_empty_ratio = non_empty_count * 1.0 / num_records
		weight.append(non_empty_ratio + selectivity)
	return weight

def select_features(ltable, rtable):
	lcolumns = ltable.columns
	rcolumns = rtable.columns
	lkey = ltable.get_key()
	rkey = rtable.get_key()
	lkey_index = -1
	rkey_index = -1
	if len(lcolumns) != len(rcolumns):
		raise StandardError('Error: FILTERED ltable and FILTERED rtable have different number of fields!')
	for i in range(len(lcolumns)):
		if lkey == lcolumns[i]:
			lkey_index = i
	if lkey_index < 0:
		raise StandardError('Error: cannot find key in the FILTERED ltable schema!')
	for i in range(len(rcolumns)):
		if rkey == rcolumns[i]:
			rkey_index = i
	if rkey_index < 0:
		raise StandardError('Error: cannot find key in the FILTERED rtable schema!')

	lweight = get_feature_weight(ltable)
	#logging.info('\nFinish calculate ltable feature weights.')
	rweight = get_feature_weight(rtable)
	#logging.info('\nFinish calculate rtable feature weights.')
	if len(lweight) != len(rweight):
		raise StandardError('Error: ltable and rtable don\'t have the same schema')

	Rank = namedtuple('Rank', ['index', 'weight'])
	rank_list = []
	for i in range(len(lweight)):
		rank_list.append(Rank(i, lweight[i] * rweight[i]))
	if lkey_index == rkey_index:
		rank_list.pop(lkey_index)
	else:
		# Make sure we remove the index with larger value first!!!
		if lkey_index > rkey_index:
			rank_list.pop(lkey_index)
			rank_list.pop(rkey_index)
		else:
			rank_list.pop(rkey_index)
			rank_list.pop(lkey_index)

	rank_list = sorted(rank_list, key=attrgetter('weight'), reverse=True)
	rank_index_list = []
	num_selected_fields = 0
	if len(rank_list) <= 3:
		num_selected_fields = len(rank_list)
	elif len(rank_list) <= 5:
		num_selected_fields = 3
	else:
		num_selected_fields = len(rank_list) / 2 
	for i in range(num_selected_fields):
		rank_index_list.append(rank_list[i].index)
	return sorted(rank_index_list)

def build_inverted_index(table_kgram_dict):
	inverted_index = defaultdict(lambda: set([]))
	for key in table_kgram_dict:
		kgram_set = table_kgram_dict[key]
		for kgram in kgram_set:
			if kgram not in inverted_index:
				inverted_index[kgram] = set([key])
			else:
				inverted_index[kgram].add(key)

	#logging.info('\nFinish building inverted index')

	return inverted_index

def get_potential_match_set(kgram_set, inverted_index):
	sets = map(lambda x: inverted_index[x], kgram_set)
	return set.union(*sets)

def main():
	#ltable = mg.read_csv('./datasets/magellan_builtin_test/table_A.csv', key='ID')
	#rtable = mg.read_csv('./datasets/magellan_builtin_test/table_B.csv', key='ID')
	#ltable = mg.read_csv('./datasets/books_test/bowker_final_custom_id.csv', key='id')
	#rtable = mg.read_csv('./datasets/books_test/walmart_final_custom_id.csv', key='id')
	#ltable = mg.read_csv('./datasets/products_test/walmart_final_custom_id_lowercase.csv', key='id')
	#rtable = mg.read_csv('./datasets/products_test/amazon_final_custom_id_python_lowercase.csv', key='id')
	ltable = mg.read_csv('./datasets/books/BN_small.csv', key='id')
	rtable = mg.read_csv('./datasets/books/amazon_books_small.csv', key='id')
	blocker = mg.AttrEquivalenceBlocker()
	candidate_set = blocker.block_tables(ltable, rtable, 'publisher', 'publisher')
	pred_table = debug_blocker(ltable, rtable, candidate_set)

if __name__ == "__main__":
	main()
