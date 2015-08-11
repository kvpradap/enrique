# imports

__prop__ = None

from magellan.io.parsers import read_csv, load_table
from magellan.sampler.sampler import sample_one_table, sample_two_tables
from magellan.utils.helperfunctions import get_install_path, init_jvm, diff
from magellan.feature.simfunctions import _m_global_sim_fns, get_sim_funs
from magellan.feature.tokenizers import _m_global_tokenizers, get_single_arg_tokenizers
from magellan.feature.attributeutils import get_attr_corres,get_attr_types
from magellan.feature.autofeaturegen import get_features, get_features_for_blocking
from magellan.feature.addfeatures import get_feature_fn, add_feature
from magellan.core.mtable import MTable
from magellan.blocker.attr_equiv_blocker import AttrEquivalenceBlocker
from magellan.blockercombiner.blockercombiner import combine_block_outputs_via_union
from magellan.gui.mtable_gui import view, edit
from magellan.labeler.labeler import label
from magellan.feature.extractfeatures import extract_feat_vecs
from magellan.matcher.nbmatcher import NBMatcher
from magellan.matcher.dtmatcher import DTMatcher
from magellan.matcher.rfmatcher import RFMatcher
from magellan.matcherselection.mlmatcherselection import select_matcher
from magellan.matcherselection.mlmatchercombinerselection import selector_matcher_combiner


_m_current_tokenizers = None
_m_current_sim_funs = None
_m_current_attr_types_ltable = None
_m_current_attr_types_rtable = None
_m_current_corres = None