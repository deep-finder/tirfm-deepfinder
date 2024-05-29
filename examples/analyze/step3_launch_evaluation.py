import os
from pathlib import Path
import deepfinder.utils.eval as ev
import deepfinder.utils.objl as ol
import pandas
 
# dataset/ and out/ both contain one folder per image, each containing an objl.xml file
path_ground_truth = Path('dataset/')
path_pred = Path('out/')
path_out = Path('evaluation/')
path_out.mkdir(exist_ok=True, parents=True)

# Read ground truth and predicted coords:   
dset_true = {}
dset_pred = {}
for fname in path_pred.iterdir():
    if not fname.is_dir(): continue
    objl_true = ol.read_xml(str(path_ground_truth / fname.name / 'objl.xml'))
    objl_pred = ol.read_xml(str(fname / 'objl.xml'))
    
    dset_true[fname] = {'object_list': objl_true}
    dset_pred[fname] = {'object_list': objl_pred}

# Evaluate and plot global scores:
dist_thr = 4
score_thr_list=list(range(0,100,10))

evaluator = ev.Evaluator(dset_true, dset_pred, dist_thr)
evaluator.get_evaluation_wrt_detection_score(score_thr_list)

fig = ev.plot_eval(evaluator.detect_eval_list, class_label=1, score_thr_list=score_thr_list)
fig.savefig(str(path_out / 'scores.pdf'))

# Get individual scores
chosen_thr = 50
chosen_thr_idx = score_thr_list.index(chosen_thr)

eval_info = evaluator.detect_eval_list[chosen_thr_idx] 
#del eval_info['global']

pd_data = {'precision': [], 'recall': [], 'f1-score': [],}
pd_index = []
for key, value in eval_info.items():
    pd_data['precision'].append(value['pre'][1])
    pd_data['recall'].append(value['rec'][1])
    pd_data['f1-score'].append(value['f1s'][1])
    pd_index.append(key)
    
df = pandas.DataFrame(data=pd_data, index=pd_index)
df.to_csv(str(path_out / 'scores_per_sequence.csv'))