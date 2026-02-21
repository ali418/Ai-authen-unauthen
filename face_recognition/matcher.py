import numpy as np
from config import Config

class FaceMatcher:
    """فئة لمقارنة المتجهات المضمنة للوجوه"""
    
    def __init__(self, threshold=None):
        """تهيئة مقارن الوجوه
        
        Args:
            threshold (float): عتبة التشابه للتطابق
        """
        self.threshold = threshold or Config.FACE_SIMILARITY_THRESHOLD
    
    def compute_similarity(self, embedding1, embedding2, method='cosine'):
        """حساب التشابه بين متجهين مضمنين
        
        Args:
            embedding1 (numpy.ndarray): المتجه المضمن الأول
            embedding2 (numpy.ndarray): المتجه المضمن الثاني
            method (str): طريقة حساب التشابه ('cosine', 'euclidean', 'l2', 'hybrid')
            
        Returns:
            float: درجة التشابه (أعلى = أكثر تشابهًا للتشابه الجيبي والهجين، أقل = أكثر تشابهًا للمسافة الإقليدية)
        """
        if method == 'cosine':
            # حساب التشابه الجيبي (1 = متطابق تمامًا، 0 = مختلف تمامًا)
            return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        
        elif method == 'euclidean' or method == 'l2':
            # حساب المسافة الإقليدية (0 = متطابق تمامًا، أكبر = أكثر اختلافًا)
            return np.linalg.norm(embedding1 - embedding2)
            
        elif method == 'hybrid':
            # طريقة هجينة تجمع بين التشابه الجيبي والمسافة الإقليدية
            cosine_sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
            euclidean_dist = np.linalg.norm(embedding1 - embedding2)
            # تطبيع المسافة الإقليدية إلى نطاق [0, 1] ثم عكسها
            max_dist = np.sqrt(2)  # أقصى مسافة ممكنة بين متجهين مطبعين
            euclidean_sim = 1 - (euclidean_dist / max_dist)
            # الجمع بين المقياسين مع إعطاء وزن أكبر للتشابه الجيبي
            return 0.7 * cosine_sim + 0.3 * euclidean_sim
    
    def match(self, embedding, database_embeddings, method='cosine'):
        """مطابقة متجه مضمن مع قاعدة بيانات من المتجهات المضمنة
        
        Args:
            embedding (numpy.ndarray): المتجه المضمن للوجه المراد مطابقته
            database_embeddings (dict): قاموس من المتجهات المضمنة {user_id: embedding, ...}
            method (str): طريقة حساب التشابه
            
        Returns:
            tuple: (user_id, similarity) للتطابق الأفضل، أو (None, 0) إذا لم يتم العثور على تطابق
        """
        if not database_embeddings:
            return None, 0
        
        best_match = None
        best_similarity = -1 if method == 'cosine' else float('inf')
        
        for user_id, db_embedding in database_embeddings.items():
            similarity = self.compute_similarity(embedding, db_embedding, method)
            
            if method == 'cosine':
                # للتشابه الجيبي، نبحث عن أعلى قيمة
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = user_id
            else:
                # للمسافة الإقليدية، نبحث عن أقل قيمة
                if similarity < best_similarity:
                    best_similarity = similarity
                    best_match = user_id
        
        # التحقق من العتبة
        if method == 'cosine':
            if best_similarity < self.threshold:
                return None, best_similarity
        else:
            if best_similarity > self.threshold:
                return None, best_similarity
        
        return best_match, best_similarity