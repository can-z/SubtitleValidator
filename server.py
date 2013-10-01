from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug import utils
import os
import validator

UPLOAD_FOLDER = './uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def output(v):
    result = ""
    for e in v.error_list:
        result += str(e[0]) + ": " + e[1] + "\n\n"

    return result


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['subtitle_file']
        filename = utils.secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/result")
def web_main():
    v = validator.Validator("sample.srt", False)
    if not v.parse_file():
        res = output(v)
        return render_template('result.html', res=res)
    v.whitespace_check()
    v.upper_case_check()
    v.lower_case_check()
    v.double_whitespace_check()
    v.single_whitespace_check()
    v.ellipsis_check()

    v.sort_errors()

    res = output(v)
    return render_template('result.html', res=res)


if __name__ == "__main__":
    app.run(debug=True)