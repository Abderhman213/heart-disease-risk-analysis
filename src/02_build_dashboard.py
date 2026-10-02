import pandas as pd, json
df=pd.read_csv("data/heart_clean.csv"); R=json.load(open("outputs/results.json"))
rows=[]
for r in df.itertuples():
    nn=lambda v: None if pd.isna(v) else float(v)
    rows.append({"age":int(r.age),"sex":int(r.sex),"sexl":r.sex_l,"cpl":r.cp_l if isinstance(r.cp_l,str) else None,"chol":nn(r.chol),"hr":nn(r.thalach),
                 "ex":None if pd.isna(r.exang) else int(r.exang),"site":r.site,"num":int(r.num),"dis":int(r.disease)})
t=open("src/dashboard_template.html").read()
m=R["model"]
t=(t.replace("__DATA__",json.dumps(rows,separators=(",",":"))).replace("__IMP__",json.dumps(m["importance"]))
 .replace("__LR_AUC__",str(m["Logistic Regression"]["test_auc"])).replace("__LR_ACC__",f'{m["Logistic Regression"]["test_acc"]*100:.0f}%')
 .replace("__RF_AUC__",str(m["Random Forest"]["test_auc"])).replace("__RF_ACC__",f'{m["Random Forest"]["test_acc"]*100:.0f}%')
 .replace("__CHARTJS__",open("package/dist/chart.umd.js").read()))
open("dashboard/index.html","w").write(t); print(len(t))
