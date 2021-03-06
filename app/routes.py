from app import app
from flask import render_template, url_for, request, session, send_from_directory, send_file
import create_rim_weight as engine
import quantipy as qp 
import pandas as pd
import os, sys, traceback, uuid
import pyreadstat

@app.route('/')
@app.route('/index')
def index():
    # load main page
    return render_template('index.html')

@app.route('/get-meta', methods=['POST'])
def process_file():
    try:         
        uid = str(uuid.uuid4())  # use uid to track multiple instances in separate tabs/windows
        # reset and initialize session
        session[uid] = {}
        session[uid]['active'] = True
        file = request.files['file']  # .sav file user selected
        filename = file.filename
        print("name of file: " + filename)
        session[uid]['filename'] = filename
        # create temp directory if it does not exist
        if not os.path.isdir('./temp'):
            print('Creating temp directory')
            os.system(f"mkdir {'./temp'}")
        file.save('./temp/%s' %(filename))
        print("Temporary file saved")


        # read dataset from saved .sav file
        ds = qp.DataSet('data')
        ds.read_spss('./temp/' + filename, ioLocale=None, detect_dichot=False)
        

        # get file metadata
        meta_data = ds.meta()['columns'].values()
        meta_data = list(iter(meta_data))  ## try to remove this to make upload faster

        if ('uuid' not in ds.meta()['columns']):
            return {'success': 'false', 'message': 'This file does not have a uuid variable.'}

        return {'success': 'true', 'uid': uid, 'meta_data_array': meta_data, 'meta_data_obj': ds.meta()['columns']}

    except Exception as e:
        print(e)
        print(sys.exc_info()[0])
        print(traceback.print_exc())
        return {'success': 'false'}


@app.route('/compute-weights', methods=['POST'])
def compute_weights():
    req_data = request.json
    uid = req_data['uid']
    target_variables = req_data['targetVariables']
    target_mapping = req_data['targetMapping']
    grouping_variable = req_data['groupingVariable']
    weight_name = req_data['weightName']

    file_name = session[uid]['filename'] ## make special error if this doesn't exist
    try:        
        file_location, syntax_location, crosstabs, report = engine.weight_data(target_variables, target_mapping, grouping_variable, file_name, weight_name=weight_name)
        session[uid]['weighted_location'] = file_location
        session[uid]['syntax_location'] = syntax_location
        return {'success': 'true', 'location': file_location, 'syntax': syntax_location, 'crosstabs': crosstabs, 'report': report}
    except Exception as e:
        print(type(e))
        print(e)
        print(traceback.print_exc())
        return {'success': 'false'}

@app.route('/temp/<path:filename>', methods=['GET'])
def download(filename):
    # serve .sav file for user to download
    uploads = os.path.join(os.path.dirname(app.root_path), 'temp')
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)

@app.route('/close', methods=['GET','POST'])
def close_resources():
    print('Closing resources')
    uid = ''
    if request.args: 
        uid = request.args.get('uid')

    if uid:    
        original_file_name = session[uid].get('filename')
        weighted_file_name = session[uid].get('weighted_location')
        syntax_file_name = session[uid].get('syntax_location')
        
        # delete spss files
        if original_file_name:
            try:
                os.remove('./temp/' + original_file_name)
            except FileNotFoundError:
                print("This file does not exist")
        if weighted_file_name:
            try:
                os.remove(weighted_file_name)
            except FileNotFoundError:
                print("This weighted file is no longer in the folder")
        if syntax_file_name:
            try:
                os.remove(syntax_file_name)
            except FileNotFoundError:
                print("This syntax file is no longer in the folder")

        # destroy session
        session[uid] = {}

        if uid in session:
            del session[uid]
    
    print(session)

    return {'success': 'true'}