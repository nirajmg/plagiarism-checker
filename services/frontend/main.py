from flask import Blueprint, Flask, render_template, request,flash,redirect, url_for
from flask_login import login_required, current_user
from minio import Minio
from werkzeug.utils import secure_filename
import os 

main = Blueprint('main', __name__)

bucket = os.getenv('BUCKET', "plagiarism-ingestion")
s3Src = os.getenv('S3_SRC', "storage.googleapis.com")
secretId = os.getenv('SECRET_ID', "GOOG7JBEJ7GU76OUS5HTT4RI")
secretKey = os.getenv('SECRET_KEY', "CV18bXT9flzceG2RVt6TN0AvgS13cuuR6wNfX4Nv")

client = Minio(s3Src, access_key=secretId, secret_key=secretKey)


@main.route('/', methods=['GET'])
def health(): return "active"

@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, data=listFiles())


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


@main.route('/download/<file>')
@login_required
def download(file):
    object_name =   f'{current_user.email}/reports/{secure_filename(file)}'
    url = client.presigned_get_object(bucket, object_name=object_name)
    return redirect(url)

def listFiles():
    return [os.path.basename(o.object_name) for o in client.list_objects(bucket, prefix=f'{current_user.email}/reports/')]   
    