from flask import Blueprint, Flask, render_template, request,flash,redirect, url_for
from flask_login import login_required, current_user
from datetime import timedelta
from minio import Minio
import json 
from werkzeug.utils import secure_filename
import os 

main = Blueprint('main', __name__)

bucket = os.getenv('BUCKET', "plagiarism-ingestion")
s3Src = os.getenv('S3_SRC', "storage.googleapis.com")
secretId = os.getenv('SECRET_ID', "")
secretKey = os.getenv('SECRET_KEY', "")

client = Minio(s3Src, access_key=secretId, secret_key=secretKey)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/upload',methods=['POST'])
@login_required
def upload():

    if 'file' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(url_for('main.profile'))
    
    file_to_upload = request.files['file']
    if file_to_upload.filename == '':
        flash('No file uploaded', 'danger')
        return redirect(url_for('main.profile'))
    
    object_name = f'{current_user.email}/files/{secure_filename(file_to_upload.filename)}'
    result = client.put_object(bucket, object_name, file_to_upload, length=-1, part_size=10*1024*1024,) 
    flash(f'{file_to_upload.filename} was successfully uploaded', 'success')
    return redirect(url_for('main.profile'))







   

    
    