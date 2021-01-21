from app import app
from flask import render_template, url_for, request, session, send_from_directory, send_file
import create_rim_weight as engine
import quantipy as qp 
import pandas as pd
import os, sys, traceback
import pyreadstat

@app.route('/')
@app.route('/index')
def index():
    # load main page
    # reset and initialize session
    session.clear()
    session['active'] = None
    return render_template('index.html')

@app.route('/get-meta', methods=['POST'])
def process_file():
    try: 
        session['active'] = True
        file = request.files['file']  # .sav file user selected
        filename = file.filename
        session['filename'] = filename
        # create temp directory if it does not exist
        if not os.path.isdir('./temp'):
            print('Creating temp directory')
            os.system(f"mkdir {'./temp'}")
        file.save('./temp/%s' %(filename))
        print("Temporary file saved")


        ### NEW
        # ds = qp.DataSet('data')
        # df, meta = pyreadstat.read_sav('./temp/' + filename)
        # #df = pd.read_spss('./temp/' + filename, convert_categoricals=False)
        # meta = meta.variable_value_labels
        # new_meta = {'info': {'columns': {}}, 'lib': {'default text': 'en-GB', 'values': {}}, 'columns': {}, 'masks': {},'sets': {'data file': {'text': {'en-GB': 'Variable order in source file'}, 
	    #     'items': []}} }
        # for k,v in meta.items():
        #     print(new_meta['info']['columns'])
        #     new_meta['columns'][k] = {"values": v, "name": k}
        #     new_meta['sets']['data file']['items'].append('columns@' + k)
        # meta = new_meta
        # print(meta)
        # ds.from_components(df, meta)
        ### OLD
        # read dataset from saved .sav file
        ds = qp.DataSet('data')
        ds.read_spss('./temp/' + filename, ioLocale=None)
        ###

        # get file metadata
        meta_data = ds.meta()['columns'].values()
        meta_data = list(iter(meta_data))

        return {'success': 'true', 'meta_data_array': meta_data, 'meta_data_obj': ds.meta()['columns']}

    except Exception as e:
        print(e)
        print(sys.exc_info()[0])
        print(traceback.print_exc())
        return {'success': 'false'}


@app.route('/compute-weights', methods=['POST'])
def compute_weights():
    req_data = request.json
    print(req_data)
    target_variables = req_data['targetVariables']
    target_mapping = req_data['targetMapping']
    grouping_variable = req_data['groupingVariable']

    file_name = session['filename'] ## make special error if this doesn't exist

    try:
        file_location, crosstabs, report = engine.weight_data(target_variables, target_mapping, grouping_variable, file_name)
        session['weighted_location'] = file_location
        return {'success': 'true', 'location': file_location, 'crosstabs': crosstabs, 'report': report}
    except Exception as e:
        print(type(e))
        print(e)
        return {'success': 'false'}

@app.route('/temp/<path:filename>', methods=['GET'])
def download(filename):
    # serve .sav file for user to download
    uploads = os.path.join(os.path.dirname(app.root_path), 'temp')
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)

@app.route('/close', methods=['GET', 'POST'])
def close_resources():
    print('Closing resources')
    # delete sav files
    original_file_name = session.get('filename')
    weighted_file_name = session.get('weighted_location')
    if original_file_name:
        try:
            os.remove('./temp/' + original_file_name)
        except FileNotFoundError:
            print("This file does not exist")
    if weighted_file_name:
        try:
            os.remove(weighted_file_name)
        except FileNotFoundError:
            print("This file is no longer in the folder")

    # destroy session
    session.clear()

    return {'success': 'true'}