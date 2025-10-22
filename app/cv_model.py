# app/cv_model.py
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from PIL import Image
import io
import os
from app import app
from tensorflow.keras.layers import InputLayer, Conv2D
from tensorflow.keras.saving import register_keras_serializable

# Vá InputLayer để xử lý batch_shape
@register_keras_serializable()
class PatchedInputLayer(InputLayer):
    def __init__(self, **kwargs):
        if 'batch_shape' in kwargs:
            batch_shape = kwargs.pop('batch_shape')
            kwargs['batch_size'] = batch_shape[0] if batch_shape else None
            kwargs['input_shape'] = batch_shape[1:] if batch_shape else None
        super().__init__(**kwargs)

# Vá DTypePolicy để xử lý compute_dtype và variable_dtype
@register_keras_serializable()
class PatchedDTypePolicy:
    def __init__(self, name='float32'):
        self.name = name
        self._compute_dtype = name
        self._variable_dtype = name

    @property
    def compute_dtype(self):
        return self._compute_dtype

    @property
    def variable_dtype(self):
        return self._variable_dtype

    def get_config(self):
        return {'name': self.name}

    @classmethod
    def from_config(cls, config):
        return cls(**config)

class SkinDiseaseModel:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(app.root_path, 'model_cv', 'best_skin_disease_model_final.h5')

        print("app.root_path =", app.root_path)
        print("model_path =", model_path)
        print("File tồn tại không?", os.path.exists(model_path))

        if not os.path.exists(model_path):
            print(f"Không tìm thấy file model tại: {model_path}")
            self.model = None
            return

        print("Tìm thấy model, đang load...")

        try:
            self.model = tf.keras.models.load_model(
                model_path,
                compile=False,
                custom_objects={
                    'InputLayer': PatchedInputLayer,
                    'DTypePolicy': PatchedDTypePolicy
                }
            )
            app.logger.info(f"Model load thành công từ: {model_path}")
        except Exception as e:
            app.logger.error(f"Lỗi khi load model: {e}")
            self.model = None
            return

        self.img_size = (224, 224)

        self.raw_class_names = [
            'Eczema',
            'Warts Molluscum and other Viral Infections',
            'Melanoma',
            'Atopic Dermatitis',
            'Basal Cell Carcinoma (BCC)',
            'Melanocytic Nevi (NV)',
            'Benign Keratosis-like Lesions (BKL)',
            'Psoriasis, Lichen Planus and related diseases',
            'Seborrheic Keratoses and other Benign Tumors',
            'Tinea, Ringworm, Candidiasis and other Fungal Infections'
        ]

        self.friendly_class_names = {
            'Eczema': 'Eczema (Chàm)',
            'Warts Molluscum and other Viral Infections': 'Mụn cóc, U mềm lây, Nhiễm virus',
            'Melanoma': 'Ung thư tế bào hắc tố (Melanoma)',
            'Atopic Dermatitis': 'Viêm da cơ địa',
            'Basal Cell Carcinoma (BCC)': 'Ung thư biểu mô tế bào đáy',
            'Melanocytic Nevi (NV)': 'Nốt ruồi tế bào hắc tố',
            'Benign Keratosis-like Lesions (BKL)': 'Tổn thương dạng sừng lành tính',
            'Psoriasis, Lichen Planus and related diseases': 'Vảy nến, Lichen phẳng và bệnh liên quan',
            'Seborrheic Keratoses and other Benign Tumors': 'Dày sừng bã nhờn và U lành tính',
            'Tinea, Ringworm, Candidiasis and other Fungal Infections': 'Nấm da, Nấm candida, Hắc lào'
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
            app.logger.error(f"Lỗi xử lý ảnh: {e}")
            return None

    def predict(self, img_data):
        try:
            if self.model is None:
                return "Model không khả dụng", 0.0, None

            processed_img = self.preprocess_image(img_data)
            if processed_img is None:
                return None, 0.0, None

            prediction = self.model.predict(processed_img)
            class_idx = np.argmax(prediction)
            confidence = float(np.max(prediction))  #Lấy max

            raw_class = self.raw_class_names[class_idx]
            friendly_name = self.friendly_class_names.get(raw_class, raw_class)

            return friendly_name, confidence, raw_class

        except Exception as e:
            app.logger.error(f"Lỗi dự đoán: {e}")
            return None, 0.0, None

try:
    cv_model = SkinDiseaseModel()
except Exception as e:
    app.logger.error(f"Không thể khởi tạo CV model: {e}")
    cv_model = None