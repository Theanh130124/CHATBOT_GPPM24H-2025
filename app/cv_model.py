# cv_model.py
import tensorflow as tf
import numpy as np
from keras_preprocessing import image
from PIL import Image
import io
import os
from app import app


class SkinDiseaseModel:
    def __init__(self, model_path='best_skin_disease_model_final.keras'):

        try:
            # Thử load model với các tùy chọn tương thích
            self.model = tf.keras.models.load_model(
                model_path,
                compile=False,  # Tạm thời không compile
                safe_mode=False  # Tắt safe mode để bỏ qua một số lỗi
            )
        except Exception as e:
            app.logger.error(f"Error loading model: {e}")
            # Fallback: tạo model mới hoặc xử lý lỗi
            self.model = None
            return

        self.img_size = (224, 224)

        # Danh sách các bệnh da liễu
        self.raw_class_names = [
            '1. Eczema 1677',
            '10. Warts Molluscum and other Viral Infections - 2103',
            '2. Melanoma 15.75k',
            '3. Atopic Dermatitis - 1.25k',
            '4. Basal Cell Carcinoma (BCC) 3323',
            '5. Melanocytic Nevi (NV) - 7970',
            '6. Benign Keratosis-like Lesions (BKL) 2624',
            '7. Psoriasis pictures Lichen Planus and related diseases - 2k',
            '8. Seborrheic Keratoses and other Benign Tumors - 1.8k',
            '9. Tinea Ringworm Candidiasis and other Fungal Infections - 1.7k'
        ]

        self.friendly_class_names = {
            '1. Eczema 1677': 'Eczema (Chàm)',
            '10. Warts Molluscum and other Viral Infections - 2103': 'Mụn cóc, U mềm lây và Nhiễm virus',
            '2. Melanoma 15.75k': 'Ung thư tế bào hắc tố (Melanoma)',
            '3. Atopic Dermatitis - 1.25k': 'Viêm da cơ địa',
            '4. Basal Cell Carcinoma (BCC) 3323': 'Ung thư biểu mô tế bào đáy',
            '5. Melanocytic Nevi (NV) - 7970': 'Nốt ruồi tế bào hắc tố',
            '6. Benign Keratosis-like Lesions (BKL) 2624': 'Tổn thương dạng sừng lành tính',
            '7. Psoriasis pictures Lichen Planus and related diseases - 2k': 'Vảy nến, Lichen phẳng',
            '8. Seborrheic Keratoses and other Benign Tumors - 1.8k': 'Dày sừng bã nhờn và U lành tính',
            '9. Tinea Ringworm Candidiasis and other Fungal Infections - 1.7k': 'Nấm da, Nấm candida'
        }

    def preprocess_image(self, img_data):
        try:
            if hasattr(img_data, 'read'):
                img = Image.open(img_data)
            else:
                img = Image.open(io.BytesIO(img_data))

            if img.mode != 'RGB':
                img = img.convert('RGB')

            img = img.resize(self.img_size)
            img_array = image.img_to_array(img)
            img_array = img_array / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            return img_array

        except Exception as e:
            app.logger.error(f"Image preprocessing error: {e}")
            return None

    def get_friendly_name(self, raw_class_name):
        return self.friendly_class_names.get(raw_class_name, raw_class_name)

    def predict(self, img_data):
        try:
            if self.model is None:
                return "Model không khả dụng", 0.0, None

            processed_img = self.preprocess_image(img_data)
            if processed_img is None:
                return None, 0.0, None

            prediction = self.model.predict(processed_img)
            confidence = np.max(prediction)  #lấy max
            class_idx = np.argmax(prediction)

            if class_idx < len(self.raw_class_names):
                raw_class_name = self.raw_class_names[class_idx]
                friendly_name = self.get_friendly_name(raw_class_name)
            else:
                raw_class_name = f"Bệnh da liễu loại {class_idx}"
                friendly_name = raw_class_name

            return friendly_name, confidence, raw_class_name

        except Exception as e:
            app.logger.error(f"Prediction error: {e}")
            return None, 0.0, None


# Global CNN model instance với xử lý lỗi
try:
    cv_model = SkinDiseaseModel()
except Exception as e:
    app.logger.error(f"Failed to initialize CV model: {e}")
    cv_model = None