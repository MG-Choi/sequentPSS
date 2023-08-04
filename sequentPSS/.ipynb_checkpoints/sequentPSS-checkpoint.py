#!/usr/bin/env python
# coding: utf-8

# In[51]:


import numpy as np
import pandas as pd
import random2
import os #os의 경우 기본적으로 주어지기 때문에 setup.py에 하지 않는다.


# In[188]:


from SALib.analyze import sobol
from SALib.analyze import fast
from SALib.analyze import rbd_fast
from SALib.analyze import delta


# ## data

# In[52]:


# change path to relative path - only for publishing
current_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_directory)

path = "./sampleData/concatenated_df.csv"
simul_data = pd.read_csv(path)

oPath = "./sampleData/"
O1 = sorted(np.loadtxt(oPath + "O1.txt"))
O2 = sorted(np.loadtxt(oPath + "O2.txt"))
O3 = sorted(np.loadtxt(oPath + "O3.txt"))



# ## simulation code

# In[53]:


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

# In[54]:


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
    
    global simple_Simulation
    
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


# In[55]:


# Preprocessing (1): determining a criterion for calibration

#def prep1_criterion():

def prep1_criterion(O_list, multi_simul_df, u, k):
    '''
    As a preprocessing step, the root mean square error (RMSE) is calculated to determine the criterion for calibration.
    
    Parameters
    ----------
    O_list: list that includes observed data
    multi_simul_df: result of multiple simulation
    u: leniency index (default:0.1, too low:overfit, too high:uncertainty)
    k: the number of parameters (3)
    
    * If there are multiple y columns in multi_simul_df, they should be denoted as y1, y2, y3, y4, and so on.
    * Likewise, p column should be in the form of p1, p2, p3, p4, and so on.

    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    Examples
    --------
    >>> rmse_sel_df, multi_simul_df = prep1_criterion(O_list, multi_simul_df, u, k) 
    '''        
    
    multi_simul_df_temp = multi_simul_df.copy()
    
    # --- func for RMSE calculation ---
    def rmse(actual, predicted):
        return np.sqrt(np.mean((np.array(actual) - np.array(predicted))**2))


    # --- add combinations of y ---
    comb_columns = [col for col in multi_simul_df_temp.columns if col.startswith('p')] # if the comlumn name starts with p
    multi_simul_df_temp['comb'] = multi_simul_df_temp[comb_columns].apply(lambda row: list(row), axis=1)

    
    # --- add new columns of rmse between y columns and O_list ---
    for i, col in enumerate(multi_simul_df_temp.columns):
        if col.startswith('y'):
            col_name = 'rmse_O' + col[1:]
            # print(col[1:])
            multi_simul_df_temp[col_name] = multi_simul_df_temp[col].apply(lambda x: rmse(x, O_list[int(col[1:]) - 1]))
    
    # --- now, we need to calculate criterions for calibration for each y--- 
    # comb는 괜히 구함. 나중에 써먹기
    # 여기서는 rmse_O1, rmse_O2,... 등의 최소, 최대값을 구하고, rmse_sel_yn =  Y_j=Min(〖RMSE〗_tem )+(Max(〖RMSE〗_tem )-Min(〖RMSE〗_tem ))*μ  을 구하면 됌.
    
    # rmse_O 컬럼들 선택
    rmse_O_columns = [col for col in multi_simul_df_temp.columns if col.startswith('rmse_O')]

    # 각 rmse_O 컬럼들의 최소값과 최댓값 구하기
    min_values = multi_simul_df_temp[rmse_O_columns].min()
    max_values = multi_simul_df_temp[rmse_O_columns].max()

    # display(multi_simul_df_temp.head(2))
    
    # --- now, calculate RMSEsel for each y.
    # select rmse_O_ columns
    rmse_O_columns = [col for col in multi_simul_df_temp.columns if col.startswith('rmse_O')]

    # save the result by creating another df
    rmse_sel_df = pd.DataFrame()

    for col in rmse_O_columns:
        rmse_min = min_values[col]
        rmse_max = max_values[col]
        # print(col, rmse_min, rmse_max)
        # add the calculation result to new columns
        rmse_sel_df[col] = [rmse_min + (rmse_max - rmse_min) * u]
        rmse_sel = rmse_min + (rmse_max - rmse_min) * u
        
        # new columns for calculation
        multi_simul_df_temp[col + '_sel'] = rmse_sel
    
        

    return rmse_sel_df, multi_simul_df_temp
    
    


# ## 2) preprocessing (2) - Sorting Y and X

# In[206]:


def sorting_Y(multi_simul_df_rmse_sel):
    '''
    Count the cases where 'rmse' is smaller than 'rmse_sel'. If the counts are higher, that 'y' is calibrated first.
    
    Parameters
    ----------
    multi_simul_df_rmse_sel: result of multiple simulation that includes rmse and rmse_sel
    
    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    Examples
    --------
    >>> y_seq_df = sorting_Y(multi_simul_df_rmse_sel)
    '''          
    
    # Columns that starts with rmse_O
    rmse_cols = [col for col in multi_simul_df_rmse_sel.columns if col.startswith('rmse_O')]
    num_rmse_cols = int(len(rmse_cols)/2)
    num_rmse_cols
    
    # Count rows that satisfies the condition (rmse < rmse_sel)
    result_df = pd.DataFrame()
    
    for i in range(1, num_rmse_cols + 1):
        rmse_col = f'rmse_O{i}'
        sel_col = f'rmse_O{i}_sel'
        count = multi_simul_df_rmse_sel[multi_simul_df_rmse_sel[rmse_col] < multi_simul_df_rmse_sel[sel_col]].shape[0]
        
        y_col = f'y{i}' # y_seq_df
        # y_seq_df = y_seq_df.append({'y': y_col, 'count': count}, ignore_index=True)

        y_col = f'y{i}'
        y_seq_df = pd.DataFrame({'y': [y_col], 'count': [count]})
        result_df = pd.concat([result_df, y_seq_df], ignore_index=True)
        
    # 'count' 컬럼을 기준으로 내림차순 정렬하여 'y' 값을 출력
    sorted_y_seq_df = result_df.sort_values(by='count', ascending=False)

    print('The order of Ys:', sorted_y_seq_df['y'].to_list())
    
    return result_df


# In[221]:


def sorting_X(problem: dict, multi_simul_df_rmse_sel, GSA = 'RBD-FAST'):
    
    '''
    
    Sobol: Sobol’ Sensitivity Analysis
    FAST: Fourier Amplitude Sensitivity Test
    RBD-FAST: Random Balance Designs Fourier Amplitude Sensitivity Test
    Delta: Delta Moment-Independent Measure
    '''
    # x_array
    Xs = np.array(multi_simul_df_rmse_sel['comb'].to_list())
    
    # 'rmse_O'로 시작하고 '_sel'이 없는 컬럼들을 뽑아서 모든 값을 array로 만들어서 리스트에 저장
    rmse_o_columns = [col for col in multi_simul_df_rmse_sel.columns if col.startswith('rmse_O') and not col.endswith('_sel')]
    y_list = [np.array(multi_simul_df_rmse_sel[col]) for col in rmse_o_columns]


    Si_list = []

    for y in y_list:
        
        if GSA == 'Sobol':
            Si = sobol.analyze(problem, y)
            # print(Si['S1'])
        elif GSA == 'FAST':
            Si = fast.analyze(problem, y)
        elif GSA == 'RBD-FAST':
            Si = rbd_fast.analyze(problem, Xs, y)
        elif GSA == 'Delta':
            Si = delta.analyze(problem, Xs, y)
            
        Si_list.append(Si['S1']) # the first-order sensitivity indices
    
    # --- Now, we will return each first order sensitivity index
    # calculate average of sensitiviry indices
    averages = [sum(column) / len(column) for column in zip(*Si_list)]

    # new dataframe
    si_df = pd.DataFrame()

    # insert x1, x2, x2... into 'Xs' column
    si_df['Xs'] = [f'x{i}' for i in range(1, len(averages) + 1)]

    # calculate average of Si and put those to 'first_order_Si' column
    si_df['first_order_Si'] = averages
    
            
    # print 'x' by decending order based on 'count' column
    sorted_x_seq_df = si_df.sort_values(by='first_order_Si', ascending=False)

    print('The order of Xs:', sorted_x_seq_df['Xs'].to_list())
    
    
    return si_df




