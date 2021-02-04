import quantipy as qp 
from datetime import datetime

def test():
    """
        Purpose: Test if flask server is running
        Parameters: None
        Returns: None
    """ 

    print("test")

def add_target(target_name, name, target_dict, all_targets_arr):
    """
        Purpose: Adds a target spec to a given array of targets
        Parameters:
            target_name - the name for the target
            name - the name of the target variable
            target_dict - the targets to add to the array
            all_targets_arr - the array of targets to add to
        Returns: None
    """ 

    target_name = {}
    target_name[name] = target_dict

    all_targets_arr.append(target_name)

def create_groups(ds, var, group_array):
    """
        Purpose: Create buckets/nets for numeric variables
        Parameters:
            ds - the active quantipy dataset
            var - the name of the variable to create groups for
            group_array - an array of groupings to use, items in the array can be in the format '(13-17)' or '(13,17)'
        Returns: None
    """ 

    ds.band(var, group_array)
    print(ds)


def add_group(ds, scheme, group_label, var, val, targets):
    """
        Purpose: Add a grouping variable to the scheme
        Parameters:
            scheme - scheme to add the group to
            group_label - label for the group
            var - variable that defines group
            val - value that defines group
            targets - targets to use for the group
        Returns: None
    """ 
  
    filter = "%s == %s" %(var, val)  # filter expression
    group_targets = redistribute_target_pcts(ds, var, val, targets)
    print("GROUP TARGETS:")
    print(group_targets)
    scheme.add_group(name=group_label, filter_def=filter, targets=targets)


def create_scheme(name="rake_scheme"):
    """
        Purpose: Create a new scheme
        Parameters:
            name - name for the scheme
        Returns: the new scheme
    """ 

    scheme = qp.Rim(name)
    return scheme

def apply_targets(scheme, targets, name='basic weights'):
    """
        Purpose: Apply the finished targets to the scheme
        Parameters:
            scheme - scheme to apply the targets to
            targets - array of targets
            name - name for the group of variables
        Returns: None
    """ 

    assert len(targets) > 0 ## there must be at least 1 target variable
    scheme.set_targets(targets=targets, group_name=name)

def save_file(ds, path):
    """
        Purpose: Save the quantipy dataset to an .sav file
        Parameters:
            ds - the active quantipy dataset
            path - location to save the file to
        Returns: None
    """

    ds.write_spss(path)

def save_syntax_file(ds, path):
    """
        Purpose: Save a syntax file that can be run to re-create weight
        Parameters:
            ds - the active quantipy dataset
            path - location to save the file to
        Returns: None
    """

    print(path)
    with open(path, 'w') as f:
        for row in ds[['uuid', 'weight']].itertuples():
            f.write("if (uuid='%s') weight=%03.20f.\n" %(row.uuid, row.weight))

def weight_data(variables, mapping, grouping, file_name, weight_name="weight"):
    """
        Purpose: Takes variables, groupings and uses them to weight the dataset
        Parameters:
            variables - array of variables to use for weighting
            mapping - dict with weighting targets for each variable in variables array
            grouping - None or a metadata dict for a variable to group by
            file_name - name of original data file
            weight_name - name for weight variable
        Returns: 
            file_location - location to save weighted file to
            syntax_location - location to save syntax file to
            crosstabs - unweighted and weighted crosstabs of variables used to set targets
            report - weighting summary
    """ 

    ds = qp.DataSet('data')
    ds.read_spss('./temp/' + file_name, ioLocale=None, detect_dichot=False)

    scheme = create_scheme("rake_scheme")
    
    ### ADD TARGETS TO SCHEME
    all_targets = []
    for i in range(len(variables)): # loop through target variables
        target_var = variables[i]
        target_dict = mapping[target_var]

        str_keys = list(target_dict.keys())
        for key in str_keys:  # loop through keys and replace string key with integer key
            int_key = int(key) 
            val_copy = target_dict[key] 
            del target_dict[key] 
            target_dict[int_key] = val_copy  

        add_target("targets_"+str(i), target_var, target_dict, all_targets)
    
    apply_targets(scheme, all_targets)

    if grouping:
        grouping_var = grouping['name']
        for v in grouping['values']:
            val = v['value']
            label = list(v['text'].values())[0]
            ds_minified = ds[ variables + [grouping_var]]  ## create smaller version of ds to pass to add_group function
            add_group(ds_minified, scheme, label, grouping_var, val, all_targets)
        grouping = grouping_var
    else:
        grouping = None # set for crosstabs
    
    ds.weight(scheme, weight_name="weight", unique_key='uuid')

    ### Relabel weight
    weight_label_key = list(ds.meta()['columns']['weight']['text'])[0] ## get key from weight dict
    ds.meta()['columns']['weight']['text'][weight_label_key] = weight_name

    ### Create name for saved weighted dataset using the time it was created
    dt = str(datetime.now()).replace(':','').replace('.','')
    file_location = './temp/' + dt.replace(" ","_") + '_weighted.sav'
    syntax_location = './temp/' + dt.replace(" ","_") + '_weight.sps'

    crosstabs = check_weights(ds, variables, grouping)

    report = generate_report(scheme)

    save_file(ds, file_location)
    save_syntax_file(ds, syntax_location)

    return file_location, syntax_location, crosstabs, report

def redistribute_target_pcts(ds, var, val, targets):
    """
        Purpose: Check whether each category of grouping variable has a value for each value in target variables
        Parameters:
            ds - subset of ds with only variables needed for weighting - target and group vars
            var - grouping variable
            val - grouping value
            targets - original targets
        Returns: 
            group_targets - targets for the specific group
    """ 

    group_targets = targets.copy()

    for i in range(len(group_targets)):  ## loop through all target variables
        v = group_targets[i]
        adjusted_targets = v.copy()
        target_var = list(adjusted_targets.keys())[0] ## get variable of target
        ds_filtered = ds[ds[var] == float(val)]  ## filter ds for grouping variable and value passed in
        existing_values = ds_filtered[target_var].unique()  ## list of values for the current target variable for the current group
        value_dict = adjusted_targets[target_var].copy()
        redistribute = 0  ## how many percentage points need to be redistributed among remaining categories
        keys_to_remove = []  ## keys to remove from dictionary
        for key in value_dict.keys():
            if (key not in existing_values):  ## no one has this value in this group 
                redistribute += value_dict[key]  ## add the percentage for this group to that which should be redistributed
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del value_dict[key]  ## delete keys not in use for this group
        if (redistribute > 0):
            for key in value_dict:
                value_dict[key] += redistribute / len(value_dict)  ## add an equal proportion of the points to be redistributed to each remaining dict value
            group_targets[i] = {target_var: value_dict}

    return group_targets

def check_weights(ds, var_array, group=None, weight='weight'):
    """
        Purpose: Visually compare weighted and unweighted data
        Parameters:
            ds - active quantipy dataset
            var_array - array of variables used for weighting
            group - None or a variable weights are grouped by
            weight - name of weight
        Returns: 
            file_location - location to save weighted file to
            crosstabs - unweighted and weighted crosstabs of variables used to set targets
            report - weighting summary
    """ 

    crosstabs = ''
    
    for var in var_array:
        crosstabs += 'Unweighted\n'
        crosstabs += ds.crosstab(x=var, y=group, w=None, pct=True).to_string()
        crosstabs += '\nWeighted\n'
        crosstabs += ds.crosstab(x=var, y=group, w=weight, pct=True).to_string() + "\n\n"
    
    print(crosstabs)
    return crosstabs

def generate_report(scheme):
    """
        Purpose: Get the weighting summary
        Parameters:
            scheme - weighting scheme used
        Returns: 
            report - the weighting summary as a string
    """ 

    report = scheme.report()['basic weights']['summary'].to_string()
    return report

def main(spss_filename):
    """
        Purpose: Run program from terminal
        Parameters:
            spss_filename - name of .sav file, extension not included
        Returns: None
    """ 

    ### OPEN SPSS DATA
    # edit main() based on desired weighting scheme
    ds = qp.DataSet(spss_filename)
    ds.read_spss('./' + spss_filename, ioLocale=None, detect_dichot=False)

    scheme = create_scheme()
    
    ### ADD TARGETS TO SCHEME
    all_targets = []
    #add_target("gender_targets", "S2", {1: 50.0, 2: 50.0}, all_targets)
    add_target("age_targets", "AgeGender", {1: 25.0, 2: 25.0, 3: 25.0, 4: 25.0}, all_targets)
    apply_targets(scheme, all_targets)

    ds_group = ds[['CellXViewer', 'AgeGender']]
    add_group(ds_group, scheme, "cat 1", "CellXViewer", "0", all_targets)
    add_group(ds_group, scheme, "cat 2", "CellXViewer", "1", all_targets)
    add_group(ds_group, scheme, "cat 3", "CellXViewer", "2", all_targets)
    add_group(ds_group, scheme, "cat 4", "CellXViewer", "3", all_targets)
    add_group(ds_group, scheme, "cat 5", "CellXViewer", "4", all_targets)

    ds.weight(scheme, weight_name="weight", unique_key='uuid')

    #check_weights(ds, ['AgeGender'], group='CellXViewer')

    save_file(ds, './' + spss_filename + '_weighted.sav')
    save_syntax_file(ds, './' + spss_filename + '_syntax.sps')

if __name__ == "__main__":
    main('AETN - Lifetime - KFC - Cleaned & Merged FINAL with TA.sav')