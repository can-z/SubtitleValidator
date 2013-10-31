import os
import datetime
import shutil

from flask import Flask, request, render_template, redirect, url_for
from werkzeug import utils

from src import validator


UPLOAD_FOLDER = './uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['subtitle_file']
        filename = utils.secure_filename(f.filename)
        if filename is None or filename == "":
            return redirect("/")

        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('result',
                                filename=filename))


@app.route("/result/<filename>")
def result(filename):
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    v = validator.Validator(full_filename, False)

    try:
        if not v.parse_file():
            res = v.produce_result_file(True)
            return render_template("result.html", res=res)
        v.perform_all_checks()
        res = v.produce_result_file(False)
    except:
        logger.error("Error processing file: " + filename)
        shutil.copy(full_filename, "trouble_maker/" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" \
                                   + os.path.basename(full_filename))
        os.remove(full_filename)
        raise
    os.remove(full_filename)
    return render_template("result.html", res=res)

if __name__ == "__main__":

    import logging
    logging.basicConfig(filename='log/' + datetime.datetime.now().strftime("%Y%m%d") + ".log", \
                        level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    stderr_handler = logging.StreamHandler()
    logger.addHandler(stderr_handler)
    app.run(debug=False)