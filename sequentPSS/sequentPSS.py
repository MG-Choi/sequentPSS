#!/usr/bin/env python
# coding: utf-8

# In[75]:


import numpy as np
import pandas as pd
import random2
import os #os의 경우 기본적으로 주어지기 때문에 setup.py에 하지 않는다.


# ## data

# In[76]:


# change path to relative path - only for publishing
current_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_directory)

path = "./sampleData/concatenated_df.csv"
simul_data = pd.read_csv(path)

oPath = "./sampleData/"
O1 = pd.read_csv(oPath + 'O1.txt')
O2 = pd.read_csv(oPath + 'O2.txt')
O3 = pd.read_csv(oPath + 'O3.txt')


# ## simulation code

# In[83]:


def simple_Simulation(p1: 'int', p2: 'int', p3: 'int', n = 10):
    '''
    to make simple simulation
    
    Parameters
    ----------
    p1 : parameter 1. range: 1 to 5
    p2 : parameter 2. range: 1 to 5
    p3 : parameter 3. range: 1 to 5
    n : the number of simulation runs

    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    Examples
    --------
    >>> simple_Simulation(p1 = 1, p2 = 3, p3 = 2, n = 11)
    '''
    
    global simul_data # globally declare
   
    # select data
    condition = (simul_data['p1'] == p1) & (simul_data['p2'] == p2) & (simul_data['p3'] == p3)
    filtered_df = simul_data[condition]
    
    dfs = []
    for i in range(n): # now, extracts by #n
        
        uniq_num = random2.choice(pd.unique(filtered_df['uniq_num']))
        chosen_df = filtered_df[filtered_df['uniq_num'] == uniq_num] #filter only uniq_num
    
        # now make new simulation data
        new_data = {
            'p1': [chosen_df['p1'].iloc[0]],
            'p2': [chosen_df['p2'].iloc[0]],
            'p3': [chosen_df['p3'].iloc[0]],
            'y1': [sorted(chosen_df['y1'].tolist())],
            'y2': [sorted(chosen_df['y2'].tolist())],
            'y3': [sorted(chosen_df['y3'].tolist())]
        }
        
        chosen_df = pd.DataFrame(new_data)

        dfs.append(chosen_df) # appended chosen_df
        
    result_df = pd.concat(dfs, axis=0, ignore_index=True) 
    
    # sort the list in the columns by ascending order
    def sort_list(lst):
        return sorted(lst)

    # apply 메서드를 사용하여 각 셀의 리스트들을 오름차순으로 정렬
    result_df['y1'] = result_df['y1'].apply(sort_list)
    result_df['y2'] = result_df['y2'].apply(sort_list)
    result_df['y3'] = result_df['y3'].apply(sort_list)

    
    return result_df


# ## 1) preprocessing (1) - Determine a criterions for calibration

# In[90]:


# run multiple simulations

def multiple_simple_simulation(p1_list, p2_list, p3_list, M = 150, u = 0.1, k = 3):
    '''
    to make simple simulation results df by multiple parameters
    
    Parameters
    ----------
    p1: parameter 1. range: 1 to 5
    p2: parameter 2. range: 1 to 5
    p3: parameter 3. range: 1 to 5
    M: MonteCarlo index (default:100, too low:low accuracy, too high:computational intensity) 
    u = leniency index (default:0.1, too low:overfit, too high:uncertainty)
    k = the number of parameters (3)

    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    Examples
    --------
    >>> multi_simul_df = multiple_simple_simulation(p1_list, p2_list, p3_list, M = 150, u = 0.1, k = 3)
    '''    
    
    
    # list for saving all results dfs
    prep1_dfs = []
    
    for i in range(M*(2*k + 2)): #1200 times
        # set parameter space
        p_1 = random2.choice(p1_list)
        p_2 = random2.choice(p2_list)
        p_3 = random2.choice(p3_list)

        # run model and save
        tem_prep1_data = simple_Simulation(p1 = p_1, p2 = p_2, p3 = p_3, n = 1)

        # append temporal result to list
        prep1_dfs.append(tem_prep1_data)

    result_df = pd.concat(prep1_dfs, axis=0, ignore_index=True)

    return result_df


# In[ ]:


# Preprocessing (1): determining a criterion for calibration



# In[89]:



