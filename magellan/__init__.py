# imports

__prop__ = True

from magellan.io.parsers import read_csv
from magellan.sampler.sampler import sample_table, down_sample
from magellan.utils.helperfunctions import get_install_path, init_jvm, diff, \
    load_dataset, load_object, save_object, apply_arbitrary_function
from magellan.utils.ast_test import get_workflow, draw_workflow
from magellan.feature.simfunctions import _global_sim_fns, get_sim_funs
from magellan.feature.tokenizers import _global_tokenizers, get_single_arg_tokenizers
from magellan.feature.attributeutils import get_attr_corres,get_attr_types
from magellan.feature.autofeaturegen import get_features, get_features_for_blocking, get_features_for_matching
from magellan.feature.addfeatures import get_feature_fn, add_feature
from magellan.core.mtable import MTable
from magellan.blocker.attr_equiv_blocker import AttrEquivalenceBlocker
from magellan.blocker.rule_based_blocker import RuleBasedBlocker
from magellan.blocker.black_box_blocker import BlackBoxBlocker
from magellan.blockercombiner.blockercombiner import combine_block_outputs_via_union
from magellan.gui.mtable_gui import view, edit
from magellan.labeler.labeler import label
from magellan.feature.extractfeatures import extract_feat_vecs
from magellan.matcher.nbmatcher import NBMatcher
from magellan.matcher.dtmatcher import DTMatcher
from magellan.matcher.rfmatcher import RFMatcher
from magellan.matcher.linregmatcher import LinRegMatcher
from magellan.matcher.logregmatcher import LogRegMatcher
from magellan.matcher.svmmatcher import SVMMatcher
from magellan.matcher.booleanrulematcher import BooleanRuleMatcher
from magellan.matcherselection.mlmatcherselection__ import select_matcher
from magellan.matcherselection.mlmatchercombinerselection import selector_matcher_combiner
from magellan.debug.debug_decisiontree_matcher import debug_decisiontree_matcher, visualize_tree
from magellan.debug.debug_randomforest_matcher import debug_randomforest_matcher
from magellan.debug.debug_booleanrule_matcher import debug_booleanrule_matcher
from magellan.trigger.matchtrigger import MatchTrigger
from magellan.evaluation.evaluation import evaluate



# _current_tokenizers = None
# _current_sim_funs = None
# _current_attr_types_ltable = None
# _current_attr_types_rtable = None
# _current_corres = None

_block_t = None
_block_s = None
_block_atypes1 = None
_block_atypes2 = None
_block_c = None

_match_t = None
_match_s = None
_match_atypes1 = None
_match_atypes2 = None
_match_c = None
