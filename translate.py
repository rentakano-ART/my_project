import requests
import csv

# DeepL APIキーを設定（ここはあなたのAPIキーに置き換えてください）
DEEPL_API_KEY = "cba57b06-dc6a-4717-9f0f-692cebc7c31b:fx"  # 実際のAPIキーに置き換える

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

# 辞書を読み込む
translation_dict = load_translation_dict('translation_dict.csv')

# 翻訳したいテキスト
text = "この作品は漆芸と陶芸を組み合わせています。"

# 辞書を使って特定の単語を強制的に変換
for japanese, english in translation_dict.items():
    text = text.replace(japanese, english)  # 辞書に基づいて日本語を英語に置き換える

# 置き換え後のテキストを表示（確認）
print(f"置き換え後のテキスト: {text}")

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

# 結果を表示
if response.status_code == 200:
    translated_text = response.json()["translations"][0]["text"]
    print(f"翻訳結果: {translated_text}")
else:
    print(f"エラー: {response.status_code} - {response.text}")
