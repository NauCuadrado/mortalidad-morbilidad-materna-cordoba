# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, confusion_matrix, recall_score, precision_score, brier_score_loss
from sklearn.inspection import permutation_importance
np.random.seed(42)

b=pd.read_pickle("_base.pkl").copy()
b["edad"]=pd.to_numeric(b["edad"],errors="coerce")
b["semanas_gestacion"]=pd.to_numeric(b["semanas_gestacion"],errors="coerce")
b["sem_falta"]=b["semanas_gestacion"].isna().astype(int)
b["anio"]=b["anio"].astype(int); b["semana"]=pd.to_numeric(b["semana"],errors="coerce")
CATc=["pertenencia_etnica","regimen","area_residencia","gestante","hospitalizada","subregion"]
for c in CATc: b[c]=b[c].replace("","Sin dato").fillna("Sin dato").astype(str)
NUM=["edad","semanas_gestacion","sem_falta","anio","semana"]
y=b["desenlace_fallecio"].values

tr=b["anio"]<=2021; te=b["anio"]>=2022
print("Train n=%d muertes=%d | Test n=%d muertes=%d"%(tr.sum(),y[tr.values].sum(),te.sum(),y[te.values].sum()))

pre=ColumnTransformer([
 ("num",Pipeline([("imp",SimpleImputer(strategy="median")),("sc",StandardScaler())]),NUM),
 ("cat",OneHotEncoder(handle_unknown="ignore",min_frequency=20),CATc)])

def evalu(nombre,clf,Xtr,ytr,Xte,yte):
    clf.fit(Xtr,ytr)
    p=clf.predict_proba(Xte)[:,1]
    auc=roc_auc_score(yte,p); ap=average_precision_score(yte,p)
    # umbral por prevalencia (top ~ tasa base*?) usamos umbral que iguala sensibilidad razonable
    thr=np.quantile(p,0.80)  # marca 20% de mayor riesgo
    pred=(p>=thr).astype(int)
    sens=recall_score(yte,pred); ppv=precision_score(yte,pred,zero_division=0)
    tn,fp,fn,tp=confusion_matrix(yte,pred).ravel()
    esp=tn/(tn+fp); brier=brier_score_loss(yte,p)
    print(f"\n[{nombre}] AUC-ROC={auc:.3f} | AUC-PR={ap:.3f} | Brier={brier:.4f}")
    print(f"   Umbral=top20% riesgo: Sens={sens:.2f} Esp={esp:.2f} VPP={ppv:.2f} (TP={tp},FP={fp},FN={fn})")
    return {"modelo":nombre,"AUC_ROC":round(auc,3),"AUC_PR":round(ap,3),"Brier":round(brier,4),
            "Sensibilidad":round(sens,2),"Especificidad":round(esp,2),"VPP":round(ppv,2)}

X=b[NUM+CATc]
Xtr,Xte=X[tr],X[te]; ytr,yte=y[tr.values],y[te.values]

res=[]
log=Pipeline([("pre",pre),("clf",LogisticRegression(max_iter=2000,class_weight="balanced"))])
res.append(evalu("Regresión logística",log,Xtr,ytr,Xte,yte))
# GBM con peso de clase via sample_weight
gbm=Pipeline([("pre",pre),("clf",HistGradientBoostingClassifier(max_iter=300,learning_rate=0.05,
              l2_regularization=1.0,class_weight="balanced",random_state=42))])
res.append(evalu("Potenciación de gradiente",gbm,Xtr,ytr,Xte,yte))

pd.DataFrame(res).to_pickle("_modelo_res.pkl")

# Importancia: OR de la logística
log.fit(Xtr,ytr)
ohe=log.named_steps["pre"].named_transformers_["cat"]
names=NUM+list(ohe.get_feature_names_out(CATc))
coef=log.named_steps["clf"].coef_[0]
imp=pd.DataFrame({"variable":names,"coef":coef,"OR":np.exp(coef)}).sort_values("coef",key=abs,ascending=False)
imp.to_pickle("_modelo_imp.pkl")
print("\nTop factores (OR, logística):")
print(imp.head(12).to_string(index=False))
