from app import app
from flask import render_template, url_for, request, session, send_from_directory, send_file
import create_rim_weight as engine
import quantipy as qp 
import os

@app.route('/')
@app.route('/index')
def index():
    session.clear()
    session['active'] = None
    return render_template('index.html')

@app.route('/get-meta', methods=['POST'])
def process_file():
    try: 
        session['active'] = True
        file = request.files['file']
        filename = file.filename
        session['filename'] = filename
        file.save('./temp/%s' %(filename))

        ds = qp.DataSet('data')
        ds.read_spss('./temp/' + filename, ioLocale=None)

        meta_data = ds.meta()['columns'].values()
        meta_data = list(iter(meta_data))

        return {'success': 'true', 'meta_data_array': meta_data, 'meta_data_obj': ds.meta()['columns']}

    except:
        return {'success': 'false'}


@app.route('/compute-weights', methods=['POST'])
def compute_weights():
    ## BE CAREFUL MAKING SOMEONE NOONE
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
    print("FILE NAME")
    print(filename)
    uploads = os.path.join(os.path.dirname(app.root_path), 'temp')
    print(uploads)
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)

@app.route('/close', methods=['GET', 'POST'])
def close_resources():
    print('Closing resources')
    # delete sav files
    original_file_name = session.get('filename')
    weighted_file_name = session.get('weighted_location')
    print(original_file_name)
    print(weighted_file_name)
    if original_file_name != None:
        try:
            os.remove('./temp/' + original_file_name)
        except FileNotFoundError:
            print("This file does not exist")
    if weighted_file_name != None:
        os.remove(weighted_file_name)

    # destroy session
    session.clear()

    return {'success': 'true'}