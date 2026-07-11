# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, confusion_matrix, recall_score, precision_score, brier_score_loss
np.random.seed(42)
b=pd.read_pickle("_base.pkl").copy()
b["edad"]=pd.to_numeric(b["edad"],errors="coerce")
b["anio"]=b["anio"].astype(int); b["semana"]=pd.to_numeric(b["semana"],errors="coerce")
# SOLO variables claramente antecedentes (sin circunstancias del evento)
CATc=["pertenencia_etnica","regimen","area_residencia","subregion"]
for c in CATc: b[c]=b[c].replace("","Sin dato").fillna("Sin dato").astype(str)
NUM=["edad","anio","semana"]
y=b["desenlace_fallecio"].values
tr=b["anio"]<=2021; te=b["anio"]>=2022
pre=ColumnTransformer([("num",Pipeline([("imp",SimpleImputer(strategy="median")),("sc",StandardScaler())]),NUM),
 ("cat",OneHotEncoder(handle_unknown="ignore",min_frequency=20),CATc)])
X=b[NUM+CATc]; Xtr,Xte=X[tr],X[te]; ytr,yte=y[tr.values],y[te.values]
for nombre,clf in [("Logística (conservadora)",LogisticRegression(max_iter=2000,class_weight="balanced")),
                   ("GBM (conservador)",HistGradientBoostingClassifier(max_iter=300,learning_rate=0.05,l2_regularization=1.0,class_weight="balanced",random_state=42))]:
    pipe=Pipeline([("pre",pre),("clf",clf)]); pipe.fit(Xtr,ytr)
    p=pipe.predict_proba(Xte)[:,1]
    auc=roc_auc_score(yte,p); ap=average_precision_score(yte,p)
    thr=np.quantile(p,0.80); pred=(p>=thr).astype(int)
    tn,fp,fn,tp=confusion_matrix(yte,pred).ravel()
    print(f"[{nombre}] AUC-ROC={auc:.3f} AUC-PR={ap:.3f} Sens={tp/(tp+fn):.2f} Esp={tn/(tn+fp):.2f} VPP={tp/(tp+fp) if tp+fp else 0:.2f}")
