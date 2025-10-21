import os
import math
import time
import pandas as pd
import requests
from dotenv import load_dotenv
load_dotenv()

INPUT_CSV = "dalieu_articles.csv"
TITLE_COLUMN = "title"
OUTPUT_DIR = "./output_benh_da_lieu"
BATCH_SIZE = 20
API_KEY = os.getenv("OPENAI_API_KEY_CRAWLER")
MODEL = "openai/gpt-oss-20b:free"

os.makedirs(OUTPUT_DIR, exist_ok=True)


#Đọc bệnh
df = pd.read_csv(INPUT_CSV)
if TITLE_COLUMN not in df.columns:
    raise ValueError(f"Không tìm thấy cột '{TITLE_COLUMN}' trong file CSV!")

diseases = df[TITLE_COLUMN].dropna().tolist()
print(f"Tổng số bệnh nhận diện được: {len(diseases)}")
total_parts = math.ceil(len(diseases) / BATCH_SIZE)
print(f"Sẽ chia thành {total_parts} phần (~{BATCH_SIZE} bệnh/phần)")


# Này để gọi model
def call_openrouter(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "BenhDaLieuGenerator",
            "Content-Type": "application/json",
        }
        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        if resp.status_code != 200:
            return f"[Lỗi API: {resp.status_code}] {resp.text[:200]}"
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[Lỗi khi gọi API: {e}]"


#Generate nội dung
for part in range(total_parts):
    start = part * BATCH_SIZE
    end = min((part + 1) * BATCH_SIZE, len(diseases))
    sublist = diseases[start:end]
    full_text = ""

    print(f"\nĐang xử lý phần {part + 1}/{total_parts} ({start + 1}–{end}) ...")

    for i, name in enumerate(sublist, 1):
        print(f" Bệnh {start + i}: {name}")
        prompt = f"""
        Viết bài phổ thông, dễ hiểu, theo Tây y, cho bệnh: {name}.
        Cấu trúc gồm 3 phần:
        1. Lý thuyết về bệnh (nguyên nhân, yếu tố nguy cơ, cơ chế bệnh sinh, dịch tễ học).
        2. Triệu chứng (dấu hiệu nhận biết, vùng da ảnh hưởng, biến chứng có thể gặp).
        3. Cách phòng chống & chữa trị (điều trị y khoa, chăm sóc da, phòng tái phát).
        Trình bày bằng tiếng Việt, mỗi phần khoảng 2–3 đoạn, dễ đọc, dễ hiểu.
        """

        content = call_openrouter(prompt)
        full_text += f"\n=============================\nTên bệnh: {name}\n{content}\n"

        time.sleep(2)  #sleep để tránh bị giới hạn

    # Lưu từng phần
    part_file = os.path.join(OUTPUT_DIR, f"benh_da_lieu_ai_part{part+1}.txt")
    with open(part_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Đã lưu {part_file}")


#Gộp file lại
merged_file = os.path.join(OUTPUT_DIR, "benh_da_lieu_ai_full.txt")
with open(merged_file, "w", encoding="utf-8") as f_out:
    for i in range(total_parts):
        part_file = os.path.join(OUTPUT_DIR, f"benh_da_lieu_ai_part{i+1}.txt")
        if os.path.exists(part_file):
            with open(part_file, "r", encoding="utf-8") as f_in:
                f_out.write(f_in.read())
                f_out.write("\n\n")

print(f"\n Hoàn tất! File tổng hợp: {merged_file}")
