import pandas as pd
import glob
from sklearn import metrics
import numpy as np
from scipy.optimize import fmin
from functools import partial
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler



def run_training(pred_df,fold):
    train_df = pred_df[pred_df.kfold != fold].reset_index(drop=True)
    valid_df = pred_df[pred_df.kfold == fold].reset_index(drop=True)

    xtrain = train_df[["lr_pred","lr_cnt_pred","rf_svd_pred"]].values
    xvalid = valid_df[["lr_pred","lr_cnt_pred","rf_svd_pred"]].values

    scl = StandardScaler()
    xtrain = scl.fit_transform(xtrain)
    xvalid = scl.fit_transform(xvalid)

    opt = LogisticRegression()  #LinearRegression
    opt.fit(xtrain,train_df.sentiment.values)
    preds = opt.predict_proba(xvalid)[:,1]
    auc = metrics.roc_auc_score(valid_df.sentiment.values,preds)
    print(f"{fold},{auc}")
    
    return opt.coef_



if __name__ == "__main__":
    files = glob.glob("../models_pred/*.csv")
    df=None

    for f in files:
        if df is None:
            df=pd.read_csv(f)
        else:
            temp_df = pd.read_csv(f)
            df =df.merge(temp_df,on="id",how="left")
    #print(df.head())
    targets = df.sentiment.values

    pred_cols = ["lr_pred","lr_cnt_pred","rf_svd_pred"]
    coefs = []
    for i in range(5):
        coefs.append(run_training(df,i))

    coefs = np.array(coefs)
    #print(coefs)
    coefs = np.mean(coefs,axis=0)
    print(coefs)

    wt_avg = (
        coefs[0][0]*df.lr_pred.values
        +  coefs[0][1]*df.lr_cnt_pred.values
        +  coefs[0][2]*df.rf_svd_pred.values
    )

    print("optimal auc after finding coefs:")

    print(metrics.roc_auc_score(targets,wt_avg))
   





    

