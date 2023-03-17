from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import logging
from flask_cors import CORS, cross_origin
import pymongo
logging.basicConfig(filename="scrapper.log", level=logging.INFO)
import os


app = Flask(__name__)


@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")


@app.route("/review", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        try:
            query = request.form["content"].replace(" ", "")

            save_dir = "images/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # fake user agent to avoid getting blocked by google.
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://www.google.com/",
                }
            
            response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")

            soup = BeautifulSoup(response.content, "html.parser")
            img_tags = soup.find_all("img")
            del img_tags[0]
            img_data = []
            for index, img_tag in enumerate(img_tags):
                img_url = img_tag["src"]
                image_data = requests.get(img_url).content
                mydict = {
                    "Index": index,
                    "Image": image_data
                }
                img_data.append(mydict)
                with open(os.path.join(save_dir, f"{query}_{img_tags.index(img_tag)}.jpg"), "wb") as f:
                    f.write(image_data)

            client = pymongo.MongoClient("mongodb+srv://Himraj:My$MongodB$@cluster0.prceeb8.mongodb.net/?retryWrites=true&w=majority")
            db = client["image_scrapper"]
            img_coll = db["image_scrap_data"]
            img_coll.insert_many(img_data)
            return "image loaded"
        except Exception as e:
            logging.info(e)
            return "something is wrong. Fix it b4 I fix you."
    else:
        return render_template("index.html")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
