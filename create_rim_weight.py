import quantipy as qp 
from datetime import datetime

#all_targets = []

def test():
    print("test")

def add_target(target_name, name, target_dict, all_targets_arr):
    target_name = {}
    target_name[name] = target_dict

    print(target_name)

    all_targets_arr.append(target_name)

def create_groups(ds, var, group_array):
    ds.band(var, group_array)
    print(ds)

def add_group(scheme, group_label, var, val, targets):
    filter = "%s == %s" %(var, val)
    print(filter)
    scheme.add_group(name=group_label, filter_def=filter, targets=targets)


def create_scheme(name="rake_scheme"):
    scheme = qp.Rim(name)
    return scheme

def apply_targets(scheme, targets, name='basic weights'):
    assert len(targets) > 0
    scheme.set_targets(targets=targets, group_name=name)

def save_file(ds, path):
    ds.write_spss(path)

def weight_data(variables, mapping, grouping, file_name):
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
        grouping = None

    ds.weight(scheme, weight_name="weight", unique_key='uuid')

    dt = str(datetime.now()).replace(':','').replace('.','')
    file_location = './temp/' + dt.replace(" ","_") + '_weighted.sav'

    crosstabs = check_weights(ds, variables, grouping)

    report = generate_report(scheme)

    save_file(ds, file_location)

    return file_location, crosstabs, report

def check_weights(ds, var_array, group=None, weight='weight'):
    crosstabs = ''
    
    for var in var_array:
        crosstabs += 'Unweighted\n'
        crosstabs += ds.crosstab(x=var, y=group, w=None, pct=True).to_string()
        crosstabs += '\nWeighted\n'
        crosstabs += ds.crosstab(x=var, y=group, w=weight, pct=True).to_string() + "\n\n"
    
    print(crosstabs)
    return crosstabs

def generate_report(scheme):
    report = scheme.report()['basic weights']['summary'].to_string()
    return report

def main(spss_filename):
    ### OPEN SPSS DATA
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