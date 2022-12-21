from flask import Flask, request, redirect, send_file
from flask_cors import CORS, cross_origin

import os

wrap_up = '<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body style="background-color: black; ">'
wrap_down = '</body></html>'

suc_msg = '<h1 style="color: white; text-align: center; font-size: 5em;">Here is what you are looking for</h1>'

def get_user_output(cin):
    def get_html(page):
        return '<img src="/images/'+ page + '.png" style="width:40%;display: block; margin-left: auto; margin-right: auto; ">'
    user_output = []
    text_pages = os.listdir('text_pages') if os.path.exists('text_pages') else []
    for text_page in text_pages:
        if cin in open('text_pages/'+text_page).read():
            user_output.append(get_html(text_page.replace('.txt','')))
    return '<br/>'.join(user_output)



app = Flask(__name__)

@app.route('/')
def main():
    return '''

<body style="background-color: black; ">'
<form method="POST" action="/find">
  <input name="cin" id="cin" type="text">
  <input type="submit">
</form>
</body>
    '''

@app.route('/find', methods=['POST', 'GET'])
def find():
    if request.method == 'POST':
        cin = request.get_data().decode().split('=')[1]
        user_output = get_user_output(cin)
        if user_output:
          # TODO: Use flask specific syntax to generate html from template
          return wrap_up + suc_msg + user_output + wrap_down
        return 'No results from your querry, please try again', {"Refresh": "1; url=/"}
    return redirect ('/')


@app.route('/images/<image_name>', methods=['GET'])
def get_image(image_name):
    if request.method == 'GET':
        return send_file(f"./images/{image_name}",mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')

