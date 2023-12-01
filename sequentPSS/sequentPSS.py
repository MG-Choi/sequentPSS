#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import random2
import random
import os 


# In[2]:


from SALib.analyze import sobol
from SALib.analyze import fast
from SALib.analyze import rbd_fast
from SALib.analyze import delta


# ## data

# In[3]:


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

# In[1]:


def simple_Simulation(x1: 'int', x2: 'int', x3: 'int', n = 10):
    '''
    Conducts a simple simulation.

    Parameters
    ----------
    x1 : int
        Parameter 1. Range: 1 to 5.
    x2 : int
        Parameter 2. Range: 1 to 5.
    x3 : int
        Parameter 3. Range: 1 to 5.
    n : int, optional
        The number of simulation runs. Default is 10.

    Returns
    -------
    DataFrame
        Returns a DataFrame as a result of the simulation.

    Examples
    --------
    >>> simple_Simulation(x1 = 1, x2 = 3, x3 = 2, n = 11)
    '''
    
    global simul_data # Declare simul_data as a global variable
   
    # Select data based on the conditions
    condition = (simul_data['x1'] == x1) & (simul_data['x2'] == x2) & (simul_data['x3'] == x3)
    filtered_df = simul_data[condition]

    dfs = [] # Initialize an empty list to store DataFrames
    for i in range(n): # Iterate n times to e
        
        uniq_num = random.choice(pd.unique(filtered_df['uniq_num']))
        chosen_df = filtered_df[filtered_df['uniq_num'] == uniq_num] # Filter by unique number
    
        # Create new simulation data
        new_data = {
            'x1': [chosen_df['x1'].iloc[0]],
            'x2': [chosen_df['x2'].iloc[0]],
            'x3': [chosen_df['x3'].iloc[0]],
            'y1': [sorted(chosen_df['y1'].tolist())],
            'y2': [sorted(chosen_df['y2'].tolist())],
            'y3': [sorted(chosen_df['y3'].tolist())]
        }
        
        chosen_df = pd.DataFrame(new_data)

        dfs.append(chosen_df) # Append the chosen DataFrame to the list
        
    result_df = pd.concat(dfs, axis=0, ignore_index=True) 
    
    # Function to sort lists in ascending order
    def sort_list(lst):
        return sorted(lst)

    # Apply the sorting function to each list in the DataFrame
    result_df['y1'] = result_df['y1'].apply(sort_list)
    result_df['y2'] = result_df['y2'].apply(sort_list)
    result_df['y3'] = result_df['y3'].apply(sort_list)

    
    return result_df


# In[2]:


# run multiple simulations

def multiple_simple_simulation(x1_list, x2_list, x3_list, M = 100, k = 3):
    '''
    Runs multiple simulations with varying parameters and compiles the results.

    Parameters
    ----------
    x1_list : list
        List of values for parameter 1. Range: 1 to 5.
    x2_list : list
        List of values for parameter 2. Range: 1 to 5.
    x3_list : list
        List of values for parameter 3. Range: 1 to 5.
    M : int, optional
        Monte Carlo index. Default is 100. A lower value may reduce accuracy, while a higher value increases computational intensity.
    k : int, optional
        The number of parameters, default is 3.

    Returns
    -------
    DataFrame
        Returns a DataFrame as a result of the multiple simulations. The data is structured as a two-dimensional data structure with labeled axes.

    Examples
    --------
    >>> multi_simul_df = multiple_simple_simulation(x1_list, x2_list, x3_list, M = 150, k = 3)
    '''        
    
    global simple_Simulation # Reference the global function simple_Simulation
    
    prep1_dfs = [] # List to store the results of each simulation
    
    for i in range(M*(2*k + 2)): # Run simulations M*(2*k + 2) times
        # Randomly choose parameters from the provided lists
        x_1 = random.choice(x1_list)
        x_2 = random.choice(x2_list)
        x_3 = random.choice(x3_list)

        # Run the simulation with the chosen parameters and store the result
        tem_prep1_data = simple_Simulation(x1 = x_1, x2 = x_2, x3 = x_3, n = 1)

        # Append the result of each simulation to the list
        prep1_dfs.append(tem_prep1_data)

    result_df = pd.concat(prep1_dfs, axis=0, ignore_index=True) # Combine all results into a single DataFrame

    return result_df


# ## 1) preprocessing (1) - Determine a criterions for calibration

# In[3]:


def prep1_criterion(O_list, multi_simul_df, u, k):
    '''
    Preprocessing function to calculate the Root Mean Square Error (RMSE) for calibration criterion.

    Parameters
    ----------
    O_list : list
        List that includes observed data.
    multi_simul_df : DataFrame
        Result DataFrame from multiple simulations.
    u : float
        Leniency index (default: 0.1). A lower value may lead to overfitting, while a higher value increases uncertainty.
    k : int
        The number of parameters (default: 3).

    Notes
    -----
    - If there are multiple 'y' columns in multi_simul_df, they should be denoted as y1, y2, y3, y4, etc.
    - Correspondingly, 'p' columns should be in the form of p1, p2, p3, p4, etc.

    Returns
    -------
    tuple
        Returns a tuple of two DataFrames: rmse_sel_df (each RMSE result for O1, O2, O3, etc.) and multi_simul_df_temp (each RMSE selection result for O1, O2, O3, etc.).

    Examples
    --------
    >>> rmse_sel_df, multi_simul_df_temp = prep1_criterion(O_list, multi_simul_df, u, k) 
    '''           
    
    multi_simul_df_temp = multi_simul_df.copy()
    
    # Function to calculate RMSE
    def rmse(actual, predicted):
        return np.sqrt(np.mean((np.array(actual) - np.array(predicted))**2))


    # Add combinations of 'x' columns
    comb_columns = [col for col in multi_simul_df_temp.columns if col.startswith('x')]
    multi_simul_df_temp['comb'] = multi_simul_df_temp[comb_columns].apply(lambda row: list(row), axis=1)

    
    # Add new columns for RMSE between 'y' columns and O_list
    for i, col in enumerate(multi_simul_df_temp.columns):
        if col.startswith('y'):
            col_name = 'rmse_O' + col[1:]
            multi_simul_df_temp[col_name] = multi_simul_df_temp[col].apply(lambda x: rmse(x, O_list[int(col[1:]) - 1]))

    # --- now, we need to calculate criterions for calibration for each y--- 

    # Select 'rmse_O' columns
    rmse_O_columns = [col for col in multi_simul_df_temp.columns if col.startswith('rmse_O')]

    # Calculate min and max values for each 'rmse_O' column
    min_values = multi_simul_df_temp[rmse_O_columns].min()
    max_values = multi_simul_df_temp[rmse_O_columns].max()

    # Calculate RMSEsel for each 'y
    rmse_sel_df = pd.DataFrame()

    for col in rmse_O_columns:
        rmse_min = min_values[col]
        rmse_max = max_values[col]
        # Calculate and add the RMSEsel result to new columns
        rmse_sel_df[col] = [rmse_min + (rmse_max - rmse_min) * u]
        rmse_sel = rmse_min + (rmse_max - rmse_min) * u
        # Add new columns for RMSE selection
        multi_simul_df_temp[col + '_sel'] = rmse_sel
    

    return rmse_sel_df, multi_simul_df_temp


# ## 2) preprocessing (2) - Sorting Y and X

# In[4]:


def sorting_Y(multi_simul_df_rmse_sel):
    '''
    This function sorts the 'y' (outcomes) based on the count of instances where 'rmse' is smaller than 'rmse_sel'. 
    The 'y' variables with higher counts are calibrated first.

    Parameters
    ----------
    multi_simul_df_rmse_sel : DataFrame
        The result DataFrame from multiple simulations, including rmse and rmse_sel values.

    Returns
    -------
    DataFrame
        Returns a DataFrame with the sorted 'y' variables and their corresponding counts.

    Examples
    --------
    >>> y_seq_df = sorting_Y(multi_simul_df_rmse_sel)
    '''             
    
    # Columns that starts with rmse_O
    rmse_cols = [col for col in multi_simul_df_rmse_sel.columns if col.startswith('rmse_O')]
    num_rmse_cols = int(len(rmse_cols)/2)
    num_rmse_cols

    # Initialize DataFrame to store results
    result_df = pd.DataFrame()
    
    # Loop through each rmse_O column
    for i in range(1, num_rmse_cols + 1):
        rmse_col = f'rmse_O{i}'
        sel_col = f'rmse_O{i}_sel'
        # Count the number of rows where rmse < rmse_sel
        count = multi_simul_df_rmse_sel[multi_simul_df_rmse_sel[rmse_col] < multi_simul_df_rmse_sel[sel_col]].shape[0]
        
        # Create a new DataFrame for each 'y' and its count
        y_col = f'y{i}'
        y_seq_df = pd.DataFrame({'y': [y_col], 'count': [count]})
        # Concatenate the new DataFrame with the result DataFrame
        result_df = pd.concat([result_df, y_seq_df], ignore_index=True)
        
    # Sort the result DataFrame in descending order based on 'count'
    sorted_y_seq_df = result_df.sort_values(by='count', ascending=False)

    print('The order of Ys:', sorted_y_seq_df['y'].to_list())
    
    return result_df


# In[5]:


def sorting_X(problem: dict, multi_simul_df_rmse_sel, SA='RBD-FAST'):
    '''
    Performs sensitivity analysis on the 'X' variables using various Sensitivity Analysis (SA) methods.
    
    Parameters
    ----------
    problem : dict
        A dictionary defining the problem for sensitivity analysis.
    multi_simul_df_rmse_sel : DataFrame
        The result DataFrame from multiple simulations, including rmse values.
    SA : str, optional
        The Global Sensitivity Analysis method to use. Options are 'Sobol', 'FAST', 'RBD-FAST', and 'Delta'.
        Default is 'RBD-FAST'.

    Methods
    -------
    Sobol : Sobol’ Sensitivity Analysis
    FAST : Fourier Amplitude Sensitivity Test
    RBD-FAST : Random Balance Designs Fourier Amplitude Sensitivity Test
    Delta : Delta Moment-Independent Measure

    Returns
    -------
    DataFrame
        Returns a DataFrame with the sensitivity indices for each 'X' variable.

    Examples
    --------
    >>> si_df = sorting_X(problem, multi_simul_df_rmse_sel, SA='RBD-FAST')
    '''

    # Convert 'comb' column to numpy array
    Xs = np.array(multi_simul_df_rmse_sel['comb'].to_list())
    
    # Extract 'rmse_O' columns that do not end with '_sel' and convert their values to arrays
    rmse_o_columns = [col for col in multi_simul_df_rmse_sel.columns if col.startswith('rmse_O') and not col.endswith('_sel')]
    y_list = [np.array(multi_simul_df_rmse_sel[col]) for col in rmse_o_columns]


    Si_list = []

    # Perform sensitivity analysis using the specified GSA method
    for y in y_list:
        if SA == 'Sobol':
            Si = sobol.analyze(problem, y)
        elif SA == 'FAST':
            Si = fast.analyze(problem, y)
        elif SA == 'RBD-FAST':
            Si = rbd_fast.analyze(problem, Xs, y)
        elif SA == 'Delta':
            Si = delta.analyze(problem, Xs, y)
            
        Si_list.append(Si['S1'])  # Append the first-order sensitivity indices

    # Calculate the average of sensitivity indices
    averages = [sum(column) / len(column) for column in zip(*Si_list)]

    # Create a new DataFrame to store results
    si_df = pd.DataFrame()

    # insert x1, x2, x2... into 'Xs' column
    si_df['Xs'] = [f'x{i}' for i in range(1, len(averages) + 1)]

    # calculate average of Si and put those to 'first_order_Si' column
    si_df['first_order_Si'] = averages

    # Sort the DataFrame in descending order based on the sensitivity index
    sorted_x_seq_df = si_df.sort_values(by='first_order_Si', ascending=False)

    print('The order of Xs:', sorted_x_seq_df['Xs'].to_list())
    
    return si_df


# ## 3) Parameter space searching and calibration

# In[47]:


def fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x: str, M = 100):
    '''
    Performs multiple simulations with one of the parameters fixed.

    Parameters
    ----------
    x1_list : list
        List of values for parameter x1.
    x2_list : list
        List of values for parameter x2.
    x3_list : list
        List of values for parameter x3.
    fix_x : str
        The parameter (x1, x2, or x3) to be fixed during the simulation.
    M : int, optional
        The number of Monte Carlo simulations. Default is 100. Lower values may reduce accuracy, while higher values increase computational intensity.

    Returns
    -------
    DataFrame
        Returns a DataFrame as a result of the multiple simulations with one parameter fixed. The data is structured as a two-dimensional data structure with labeled axes.

    Examples
    --------
    >>> multi_simul_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x='x1', M=100)
    '''  
    
    global simple_Simulation # Reference the global function simple_Simulation
    
    prep1_dfs = [] # List to store the results of each simulation
    
    # Determine which parameter list to use as the fixed parameter list
    if fix_x == 'x1':
        target_list = x1_list.copy()
    elif fix_x == 'x2':
        target_list = x2_list.copy()
    elif fix_x == 'x3':
        target_list = x3_list.copy()
    
    # Iterate over each value of the fixed parameter
    for fix_param in target_list:
        for i in range(M): # Run simulations M times
            # Set parameter space based on the fixed parameter
            if fix_x == 'x1':
                x_1 = fix_param
                x_2 = random.choice(x2_list)
                x_3 = random.choice(x3_list)
            elif fix_x == 'x2':
                x_1 = random.choice(x1_list)
                x_2 = fix_param
                x_3 = random.choice(x3_list)
            elif fix_x == 'x3':
                x_1 = random.choice(x1_list)
                x_2 = random.choice(x2_list)
                x_3 = fix_param

            # Run the simulation and save the result
            tem_prep1_data = simple_Simulation(x1=x_1, x2=x_2, x3=x_3, n=1)

            # Append the result to the list
            prep1_dfs.append(tem_prep1_data)
    # Combine all results into a single DataFrame
    result_df = pd.concat(prep1_dfs, axis=0, ignore_index=True)

    return result_df


# In[6]:


def seqCalibration(fix_x, fix_y, rmse_sel, simul_result_df, O_list, t, df_return = False): #x_index는 x 몇인지, y_index는 y 몇인지
    
    '''
    Runs sequential calibration by fixing one parameter and one dependent variable.
    The permissible calibrated parameter space varies based on the tolerance index (τ). 
    A higher τ value results in stricter calibration, reducing the parameter space significantly

    Parameters
    ----------
    fix_x : str
        The fixed x parameter in the current calibration round.
    fix_y : str
        The fixed y parameter in the current calibration round.
    rmse_sel : float
        The rmse_sel value of y from the rmse_sel DataFrame.
    simul_result_df : DataFrame
        The simulation result DataFrame that includes each x and corresponding y values.
    O_list : list
        A list that includes all observed data of Y.
    t : float
        Tolerance index to determine the calibration accuracy.
    df_return : bool, optional
        Whether to return the result DataFrame (True) or just the list (False). Default is False.

    Returns
    -------
    tuple or list
        If df_return is True, returns a tuple of a new list of x values and the result DataFrame. Otherwise, returns only the new list of x values.

    Examples
    --------
    >>> x3_list, result_df = seqCalibration(fix_x='x3', fix_y='y1', rmse_sel=401.295316, simul_result_df=fix_x3_simul_result_df, O_list=O_list, t=0.1, df_return=True)
    >>> x3_list = seqCalibration(fix_x='x3', fix_y='y1', rmse_sel=401.295316, simul_result_df=fix_x3_simul_result_df, O_list=O_list, t=0.1)
    '''
    
    # Function to calculate RMSE
    def rmse(actual, predicted):
        return np.sqrt(np.mean((np.array(actual) - np.array(predicted))**2))


    # --- add combinations of y ---
    df = simul_result_df.copy()
    # Add combinations of x columns
    comb_columns = [col for col in df.columns if col.startswith('x')] # if the comlumn name starts with x
    df['comb'] = df[comb_columns].apply(lambda row: list(row), axis=1)

    # Compute RMSE for the fixed y variable
    df[fix_y + '_rmse'] = df[fix_y].apply(lambda x: rmse(x, O_list[int(fix_y[1:]) - 1])) # pull index of y and pull Observed data
    df['n_R'] = 1   # All counts of RMSE result
    df['n_C'] = 0   # ALl counts of RMSE result but lower than RMSE_sel
    
    # --- return result ---
    df.loc[df[fix_y + '_rmse'] < rmse_sel, 'n_C'] = 1 # if y1_rmse is lower than rmse_sel -> put 1 in n_C
    
    # Analyze the calibration reliability for each unique value of the fixed x parameter
    result_summary = {}
    unique_x_values = df[fix_x].unique()
    new_x_list = []
    
    for x_value in unique_x_values:   # when n_C / n_R is greater than t : save it to the list
        n_R_sum = df.loc[df[fix_x] == x_value, 'n_R'].sum()
        n_C_sum = df.loc[df[fix_x] == x_value, 'n_C'].sum()
        if n_C_sum / n_R_sum >= t:
            result_summary[x_value] = round(n_C_sum / n_R_sum, 3)
            new_x_list.append(x_value)
    
    # Print the reliability summary
    print('reliability of \'' + fix_x + '\' for \'' + fix_y + '\' (1 - uncertainty degree): ', result_summary)
    
    new_x_list = sorted(new_x_list)

    # Return the result based on df_return flag
    if df_return == True:
        return new_x_list, df
    else:
        return new_x_list

