from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import csv
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # セッションでflashメッセージを使用するために必要

# データベースの設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///translation_dict.db'  # データベースのパス
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

DEEPL_API_KEY = "cba57b06-dc6a-4717-9f0f-692cebc7c31b:fx"  # 実際のAPIキーに置き換えてください

# 翻訳辞書のデータモデル
class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    japanese = db.Column(db.String(100), nullable=False)
    english = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Translation {self.japanese} - {self.english}>'

# データベースを作成（最初に一度だけ実行）
def create_db():
    with app.app_context():
        db.create_all()

# 翻訳処理（DeepL APIを利用）
def translate_text(text):
    # 1. 翻訳辞書をデータベースから取得
    translation_dict = {t.japanese: t.english for t in Translation.query.all()}

    # 2. 辞書に登録された単語を置換
    for japanese, english in translation_dict.items():
        if japanese in text:
            text = text.replace(japanese, english)
    
    # 3. 辞書で翻訳できない部分をDeepLで翻訳
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "source_lang": "JA",  # 日本語
        "target_lang": "EN",  # 英語
    }

    response = requests.post(url, data=params)
    if response.status_code == 200:
        translated_text = response.json()["translations"][0]["text"]
        return translated_text
    else:
        return f"エラー: {response.status_code} - {response.text}"


# ホームページのルート
@app.route("/", methods=["GET", "POST"])
def home():
    translated_text = ""
    if request.method == "POST":
        input_text = request.form["text"]
        translated_text = translate_text(input_text)
    return render_template("index.html", translated_text=translated_text)

# 単語追加のフォーム
@app.route("/add_word", methods=["POST"])
def add_word():
    japanese = request.form["japanese"]
    english = request.form["english"]

    # バリデーション
    if not japanese or not english:
        return render_template("index.html", error="日本語と英語の両方を入力してください。")

    # データベースに新しい単語を追加
    new_translation = Translation(japanese=japanese, english=english)
    db.session.add(new_translation)
    db.session.commit()

    return redirect(url_for("home"))

# 単語リストの表示
@app.route("/view_dict")
def view_dict():
    # データベース内のすべての翻訳単語を取得
    translations = Translation.query.all()
    dict_list = [{'japanese': t.japanese, 'english': t.english} for t in translations]
    return render_template("view_dict.html", dict_list=dict_list)

# CSVファイルから翻訳データを読み込んでデータベースに登録
def load_csv_to_db(csv_file_path):
    with app.app_context():
        # データベースをクリアしてから再登録（必要に応じて）
        db.session.query(Translation).delete()
        
        # CSVファイルを読み込む
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                japanese = row.get("japanese")
                english = row.get("english")
                if japanese and english:
                    new_translation = Translation(japanese=japanese, english=english)
                    db.session.add(new_translation)
            db.session.commit()

# CSVファイルアップロード用のルート
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/upload_csv", methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        if "file" not in request.files:
            flash("ファイルが選択されていません。")
            return redirect(request.url)
        
        file = request.files["file"]
        if file.filename == "":
            flash("有効なファイルを選択してください。")
            return redirect(request.url)

        # CSVファイルを保存
        if file:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            # データベースに反映
            load_csv_to_db(file_path)
            flash("CSVファイルが正常にアップロードされ、翻訳辞書が更新されました。")
            return redirect(url_for("home"))
    
    return render_template("upload_csv.html")

if __name__ == "__main__":
    # 初回実行時にデータベースを作成
    create_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
