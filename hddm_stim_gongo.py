# -*- coding: utf-8 -*-
"""
Created on Wed May 17 16:57:37 2017
Adapted form the hddm tutorial http://ski.clps.brown.edu/hddm_docs/tutorial_regression_stimcoding.html
Assume a 2x2 within-subject design
    Go/No-go and Session1/Session2
@author: sapjz
"""

import hddm
from patsy import dmatrix  # for generation of (regression) design matrices
import numpy as np         # for basic matrix operations
from pandas import Series  # to manipulate data-frames generated by hddm

n_subjects = 5
trials_per_level = 150 # and per stimulus

# session 1
level1a = {'v':.3, 'a':2, 't':.3, 'sv':0, 'z':.6, 'sz':0, 'st':0}
# level2 is the nogo condition, and therefore the v is negative here (towards the no-go boundary)
level2a = {'v':-1, 'a':2, 't':.3, 'sv':0, 'z':.4, 'sz':0, 'st':0}

data_a, params_a = hddm.generate.gen_rand_data({'go': level1a,
                                                'nogo': level2a,},
                                                size=trials_per_level,
                                                subjs=n_subjects)

# session 2
level1b = {'v':.6, 'a':1.5, 't':.2,'sv': 0, 'z':.7, 'sz': 0, 'st': 0}
level2b = {'v':-1.5, 'a':1.5, 't':.2,'sv': 0, 'z':.3, 'sz': 0, 'st': 0}

data_b, params_b = hddm.generate.gen_rand_data({'go': level1b,
                                                'nogo': level2b,},
                                                size=trials_per_level,
                                                subjs=n_subjects)

data_a['session'] = Series(np.ones((len(data_a))), index=data_a.index)
data_b['session'] = Series(np.ones((len(data_b)))*2, index=data_a.index)

# we expect v to change between sessions and between go/no-go conditions
data_a['cond_v'] = data_a.condition.str.cat(data_a.session.astype(np.int64).apply(str))
data_b['cond_v'] = data_b.condition.str.cat(data_b.session.astype(np.int64).apply(str))

mydata = data_a.append(data_b, ignore_index=True)

# set noResponse RT to -1, not necessary, but jsut to make things clear
mydata.rt[mydata.response == 0] = -1

mydata.to_csv('mydata.csv')

def z_link_func(x, data=mydata):
    stim = (np.asarray(dmatrix('0 + C(s, [[1], [-1]])',
                               {'s': data.session.ix[x.index]}))
    )
    return 1 / (1 + np.exp(-(x * stim)))

# if you assume other parameter changes as well, we need to add other parameters
z_reg = {'model': 'z ~ 1 + C(session)', 'link_func': z_link_func}
v_reg = {'model': 'v ~ 1 + C(cond_v)', 'link_func': lambda x: x}
a_reg = {'model': 'a ~ 1 + C(session)', 'link_func': lambda a: a}
t_reg = {'model': 't ~ 1 + C(session)', 'link_func': lambda t: t}

reg_descr = [z_reg, v_reg, a_reg, t_reg]
m_reg = hddm.HDDMRegressor(mydata, reg_descr, include='z')

m_reg.sample(2000, burn=200)

m_reg.print_stats() # check the outputs in comparision with the true param

"""
Example of one run. 
Note that the z values should be passed through the transition function to get its face values.
                          mean        std       2.5q        25q        50q       75q     97.5q       mc err
z_Intercept           0.346673  0.0564847   0.239106   0.307751     0.3441  0.386205  0.461575   0.00439742
z_Intercept_std       0.211743  0.0405919   0.124576   0.186462   0.212431  0.240409  0.289452   0.00228978
z_Intercept_subj.0    0.468137   0.076576   0.313579   0.416551   0.469894  0.523116   0.61058   0.00546733
z_Intercept_subj.1      0.2409  0.0505806   0.150262   0.204568   0.238209  0.273871  0.346782   0.00324306
z_Intercept_subj.2    0.271563  0.0573848   0.166577   0.230793   0.269063  0.311191   0.38972   0.00391868
z_Intercept_subj.3    0.310187  0.0620826   0.195229   0.267373   0.306494  0.353033  0.431924   0.00445056
z_Intercept_subj.4     0.44693  0.0736314   0.298593   0.395914   0.449606  0.499134  0.589479   0.00533299
z_C(session)[T.2.0]  -0.747035   0.149815   -1.00368  -0.853931   -0.75911  -0.65343 -0.405417    0.0126088
v_Intercept            0.40884   0.119403   0.163848   0.342015   0.404791  0.473467  0.659351   0.00406407
v_Intercept_std         0.2066    0.12635   0.064433   0.126097   0.174526  0.252869   0.55676   0.00568009
v_Intercept_subj.0    0.264072  0.0711253   0.128652   0.215637   0.264595  0.309564  0.403086   0.00345553
v_Intercept_subj.1    0.414372  0.0715001   0.268727   0.369005   0.414065  0.463023   0.55052   0.00309055
v_Intercept_subj.2     0.59832  0.0840216   0.426102   0.541955   0.599277  0.655588  0.768225    0.0038385
v_Intercept_subj.3    0.415052  0.0715428   0.282286   0.363137   0.413303  0.464479  0.558555   0.00344218
v_Intercept_subj.4    0.329264  0.0749482   0.183207   0.280229   0.330535  0.380806  0.475904   0.00348097
v_C(cond_v)[T.go2]    0.385051   0.137392   0.128313   0.291263   0.381375  0.471719  0.679809     0.010247
v_C(cond_v)[T.nogo1]  -1.74283  0.0776232   -1.89234   -1.79724   -1.74164  -1.68926  -1.59147   0.00286797
v_C(cond_v)[T.nogo2]  -2.90649   0.169356   -3.22299   -3.02155   -2.90799  -2.79034  -2.56435    0.0104097
a_Intercept            2.11514   0.143712    1.85965    2.02601    2.11038   2.18617   2.44977   0.00585757
a_Intercept_std       0.267584   0.159312  0.0991149   0.164557   0.223291  0.319768   0.69504   0.00644995
a_Intercept_subj.0     2.35081  0.0790306    2.19834     2.2965    2.35103   2.40267   2.50895   0.00439321
a_Intercept_subj.1     2.01399  0.0656827    1.89115    1.96844    2.01179   2.05876   2.14611   0.00412558
a_Intercept_subj.2     1.92823  0.0749201    1.79621    1.87649     1.9218   1.97856   2.08789   0.00519325
a_Intercept_subj.3     2.05542  0.0692842    1.91864    2.00723    2.05535   2.10082   2.19216   0.00428725
a_Intercept_subj.4     2.20608  0.0782418    2.05521     2.1526     2.2051   2.25517   2.36135   0.00513966
a_C(session)[T.2.0]  -0.683105  0.0684222  -0.820286  -0.727738  -0.687073 -0.634711 -0.552473   0.00522558
t_Intercept           0.348954  0.0578091   0.256088   0.313574   0.342387  0.373827  0.489879   0.00241531
t_Intercept_std       0.115675  0.0716851  0.0479778  0.0729371  0.0956295  0.133578  0.290729    0.0037631
t_Intercept_subj.0    0.338424   0.012289   0.312781   0.330424   0.339155  0.346913  0.360888  0.000548951
t_Intercept_subj.1    0.230491  0.0129194   0.205673   0.220674   0.230349    0.2405  0.254102   0.00106308
t_Intercept_subj.2    0.340683  0.0110646   0.318427   0.333152    0.34061  0.348867  0.361432  0.000819053
t_Intercept_subj.3    0.429096  0.0109785   0.406575    0.42145   0.429563  0.437048  0.449291  0.000752518
t_Intercept_subj.4    0.315421  0.0145723   0.288236    0.30473   0.315293  0.325572  0.343437   0.00114481
t_C(session)[T.2.0]  -0.187779  0.0140875  -0.217928  -0.198076  -0.186927 -0.177364 -0.162839   0.00125402
DIC: 2962.471799
deviance: 2938.642003
pD: 23.829796
"""


