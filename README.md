# Latitude RIM Weighter

## This program will compute RIM weights for a given dataset.

1. Edit the main method of create_rim_weight.py
2. Run the flask server (<code>flask run</code>) to use a GUI

Dependencies can be installed from requirements.txt <code>pip install -r "requirements.txt"</code>, with the exception of Quantipy which was manually edited. The edited version is saved in the Lib folder. An extra parameter detect_dichot was added to the parse_sav_file method in reader.py. This should be set to false.

If a target is set to 0% for a non-empty group, the weights will not be accurate. E.g., if 30% of respondents are Female, weighting that group to 0% will produce unexpected results.

The data file used <i>MUST</i> include the uuid variable.