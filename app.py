from flask import Flask, render_template, request
import csv
import requests

app = Flask(__name__)

# DeepL APIキーを設定
DEEPL_API_KEY = "cba57b06-dc6a-4717-9f0f-692cebc7c31b:fx"  # 実際のAPIキーを入力

# 翻訳辞書（CSVファイル）を読み込む
def load_translation_dict(file_path):
    translation_dict = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # 空行をスキップ
                japanese, english = row
                translation_dict[japanese] = english
    return translation_dict

# 翻訳辞書を読み込む
translation_dict = load_translation_dict('translation_dict.csv')

# 翻訳処理
def translate_text(text):
    # 辞書を使って特定の単語を強制的に変換
    for japanese, english in translation_dict.items():
        text = text.replace(japanese, english)

    # DeepL APIリクエストの設定
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "source_lang": "JA",  # 翻訳元言語（日本語）
        "target_lang": "EN"   # 翻訳先言語（英語）
    }

    # リクエストを送信
    response = requests.post(url, data=params)
    
    if response.status_code == 200:
        translated_text = response.json()["translations"][0]["text"]
        return translated_text
    else:
        return f"エラー: {response.status_code} - {response.text}"

@app.route("/", methods=["GET", "POST"])
def home():
    translated_text = ""
    if request.method == "POST":
        # フォームから入力されたテキストを取得
        input_text = request.form["text"]
        # 翻訳実行
        translated_text = translate_text(input_text)
    return render_template("index.html", translated_text=translated_text)

if __name__ == "__main__":
    app.run(debug=True)
