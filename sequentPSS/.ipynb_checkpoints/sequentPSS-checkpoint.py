#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import random2


# ## data

# In[2]:


path = './sampleData/'
simul_data = pd.read_csv(path + 'concatenated_df.csv')


# ## simulation code

# In[3]:


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
    
    return result_df


# ## 1) preprocessing (1)

# In[1]:


def criterion(asd):
    print(asd + "asdasdasdccqc")


# In[ ]:




