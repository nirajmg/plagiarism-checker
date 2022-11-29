import datetime

from flask import Flask, render_template
from google.cloud import storage

app = Flask(__name__)


bucket_name = os.getenv("BUCKET_NAME") or "default-name"
destination_blob_name = os.getenv("BLOB_NAME") or "default-blobname"

@app.route('/')
def root():

    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
	storage_client = storage.Client()
	extension = secure_filename(uploaded_file.filename).rsplit('.', 1)[1]
    	bucket = storage_client.bucket(bucket_name)
    	blob = bucket.blob(destination_blob_name)
    	blob.upload_from_filename(source_file_name)
    	print(
        	"File {} uploaded to {}.".format(
        	source_file_name, destination_blob_name
       		)
    	)
	#return jsonify({"success": True})
    except Exception as e:
    	logging.exception(e)
        #return jsonify({"success": False})
    return redirect(url_for('index')) # Pick one or the other 
    

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
