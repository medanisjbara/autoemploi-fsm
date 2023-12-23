from flask import Flask, redirect, render_template, request, send_file
from fetch_utils import get_cropped_docs

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("search.html")


@app.route("/find", methods=["POST", "GET"])
def find():
    if request.method == "POST":
        cin = request.get_data().decode().split("=")[1]
        if not cin:
            return redirect("/")
        needed_images = get_cropped_docs(cin.replace("+", " "))
        if needed_images:
            return render_template(
                "result.html", docs=needed_images, len=len(needed_images)
            )
        return render_template("not_found.html")
    return redirect("/")


@app.route("/images/<image_name>", methods=["GET"])
def get_image(image_name):
    image_name = image_name.replace(" ", "%20")
    if request.method == "GET":
        return send_file(f"./images/{image_name}", mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
