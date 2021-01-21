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


def add_group(scheme, group_label, var, val, targets):
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

def weight_data(variables, mapping, grouping, file_name):
    """
        Purpose: Takes variables, groupings and uses them to weight the dataset
        Parameters:
            variables - array of variables to use for weighting
            mapping - dict with weighting targets for each variable in variables array
            grouping - None or a metadata dict for a variable to group by
            file_name - name of original data file
        Returns: 
            file_location - location to save weighted file to
            crosstabs - unweighted and weighted crosstabs of variables used to set targets
            report - weighting summary
    """ 

    ds = qp.DataSet('data')
    ds.read_spss('./temp/' + file_name, ioLocale=None)

    scheme = create_scheme("rake_scheme")
    
    ### ADD TARGETS TO SCHEME
    all_targets = []
    
    for i in range(len(variables)): # loop through target variables
        target_var = variables[i]
        target_dict = mapping[target_var]

        for key in target_dict.keys():  # loop through keys and replace string key with integer key
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
            add_group(scheme, label, grouping_var, val, all_targets)
        grouping = grouping_var
    else:
        grouping = None # set for crosstabs

    ds.weight(scheme, weight_name="weight", unique_key='uuid')

    ### Create name for saved weighted dataset using the time it was created
    dt = str(datetime.now()).replace(':','').replace('.','')
    file_location = './temp/' + dt.replace(" ","_") + '_weighted.sav'

    crosstabs = check_weights(ds, variables, grouping)

    report = generate_report(scheme)

    save_file(ds, file_location)

    return file_location, crosstabs, report

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
    ds.read_spss('./' + spss_filename + '.sav', ioLocale=None)

    scheme = create_scheme()
    
    ### ADD TARGETS TO SCHEME
    all_targets = []
    #add_target("gender_targets", "S2", {1: 50.0, 2: 50.0}, all_targets)
    add_target("age_targets", "S1", {1: 50.0, 2: 50.0}, all_targets)
    apply_targets(scheme, all_targets)

    add_group(scheme, "cat 1", "S2", "1", all_targets)
    add_group(scheme, "cat 2", "S2", "2", all_targets)

    ds.weight(scheme, weight_name="weight", unique_key='uuid')

    check_weights(ds, ['S1', 'S2', 'fam'], group='S2')

    save_file(ds, './' + spss_filename + '_weighted.sav')

if __name__ == "__main__":
    main('data')