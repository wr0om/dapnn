# AUTOGENERATED! DO NOT EDIT! File to edit: 05_performance.ipynb (unless otherwise specified).

__all__ = ['load_pred_model', 'inference']

# Cell
from .imports import *
from .data_processing import *

from .anomaly import *

# Cell
import warnings
warnings.filterwarnings(action='once')

# Cell
def load_pred_model(learner_path,train_log_path,log_name,cols=['activity']):
    log = import_log(train_log_path)
    o,dls,categorify = training_dl(log,cat_names=cols)
    loss=partial(multi_loss_sum,o)
    emb_szs = get_emb_sz(o)
    m=MultivariateModel(emb_szs)
    learn=Learner(dls, m, path=learner_path, model_dir='.', loss_func=loss, metrics=get_metrics(o))
    learn.load(log_name,with_opt=False)
    m=learn.model.cuda()
    return m, categorify

def inference(test_log_path,m,categorify,log_name,cols=['activity'],fixed_threshold=None,override_threshold_func=None):
    if type(test_log_path)==str:
        log = import_log(test_log_path)
    else:
        log = test_log_path
    o = process_test(log,categorify,cols)
    nsp,idx=predict_next_step(o,m)
    score_df=multivariate_anomaly_score(nsp,o,idx,cols)
    y_true,y_pred=multivariate_anomalies(score_df,cols,idx,o,fixed_threshold=fixed_threshold)
    if override_threshold_func is not None:
        y_true,y_pred=multivariate_anomalies(score_df,cols,idx,o,get_thresholds=override_threshold_func)
    else:
        y_true,y_pred=multivariate_anomalies(score_df,cols,idx,o,fixed_threshold=fixed_threshold)
    f1_score(y_true, y_pred)
    nsp_acc= float(nsp_accuracy(o,idx,nsp[0]))
    f1 = f1_score(y_true, y_pred)
    acc = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true,y_pred)
    recall = recall_score(y_true,y_pred)
    return [log_name, nsp_acc, f1, acc, precision, recall]