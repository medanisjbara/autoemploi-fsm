from flask import Flask, redirect, render_template, request, send_file
from fetch_utils import get_cropped_docs

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("search.html")


@app.route("/find", methods=["POST", "GET"])
def find():
    if request.method == "POST":
        ident = request.get_data().decode().split("=")[1]
        if not ident:
            return redirect("/")
        needed_images = get_cropped_docs(ident.replace("+", " "))
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


@app.route("/api", methods=["POST"])
def api():
    if request.method == "POST":
        if request.content_type != "application/json":
            return {"result": "unknown content type, please use application/json"}
        ident = request.get_json()["ident"]
        if not ident:
            return {"result": "no_input"}
        needed_images = get_cropped_docs(ident.replace("+", " "))
        if needed_images:
            return {
                "result": [
                    f"https://{request.host}/images/{img}" for img in needed_images
                ]
            }
        return {"result": "not_found"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
