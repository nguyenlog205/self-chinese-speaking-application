"""
Scoring Service - Business logic for pronunciation scoring.
Handles error analysis, feedback generation, and core scoring.
"""

import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher

from pypinyin import pinyin, Style
from src.core.engines.pronunciation_scorer import get_scorer

logger = logging.getLogger("scoring_service")


class ScoringService:
    def __init__(self):
        self.scorer = get_scorer()

    def score(self, audio_bytes: bytes, reference_text: str) -> Dict[str, Any]:
        """
        Score pronunciation and provide detailed error analysis.
        """
        # 1. Get transcription from core
        transcribed = self.scorer.transcribe(audio_bytes)
        if not transcribed:
            transcribed = ""

        # 2. Calculate CER
        from jiwer import cer as jiwer_cer
        error_rate = jiwer_cer(reference_text, transcribed)
        score_value = max(0, 100 - (error_rate * 100))
        score_value = round(score_value, 2)

        # 3. Pinyin-based error analysis
        details = self._pinyin_analysis(reference_text, transcribed)

        # 4. Enhanced feedback
        feedback = self._generate_feedback(details, score_value)

        return {
            "score": score_value,
            "wer": round(error_rate, 4),
            "transcribed": transcribed,
            "reference": reference_text,
            "feedback": feedback,
            "details": details
        }

    def _pinyin_analysis(self, ref: str, trans: str) -> List[Dict]:
        """
        Compare pinyin of reference and transcription syllable by syllable.
        """
        # Lấy pinyin cho reference
        ref_pinyin = pinyin(ref, style=Style.TONE3, heteronym=False)
        # Lấy pinyin cho transcription (có thể không chính xác nếu trans không phải tiếng Trung)
        trans_pinyin = pinyin(trans, style=Style.TONE3, heteronym=False)

        # Nếu trans không có pinyin (ví dụ tiếng Việt), dùng list rỗng
        if not trans_pinyin:
            trans_pinyin = []

        # Chuẩn hóa: mỗi âm tiết là tuple (pinyin, thanh điệu)
        ref_syllables = self._parse_syllables(ref_pinyin)
        trans_syllables = self._parse_syllables(trans_pinyin)

        # Align syllables (có thể dùng SequenceMatcher)
        details = self._align_and_analyze(ref_syllables, trans_syllables)

        return details

    def _parse_syllables(self, pinyin_list: List[List[str]]) -> List[Dict]:
        """
        Parse pinyin list thành các âm tiết với thanh điệu.
        Input: [['ni3'], ['hao3']] -> [{'pinyin': 'ni3', 'tone': 3, 'initials': 'n', 'final': 'i'}]
        """
        result = []
        for p in pinyin_list:
            if not p:
                continue
            p_str = p[0]  # 'ni3'
            # Tách thanh điệu
            tone = 0
            base = p_str
            if p_str[-1].isdigit():
                tone = int(p_str[-1])
                base = p_str[:-1]
            # Tách phụ âm đầu và vần (đơn giản hóa)
            initials, final = self._split_initial_final(base)
            result.append({
                "pinyin": p_str,
                "tone": tone,
                "base": base,
                "initials": initials,
                "final": final,
                "char": ""  # sẽ điền sau nếu cần
            })
        return result

    def _split_initial_final(self, pinyin: str) -> Tuple[str, str]:
        """
        Tách phụ âm đầu và vần.
        """
        initials_list = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h',
                         'j', 'q', 'x', 'zh', 'ch', 'sh', 'r', 'z', 'c', 's', 'y', 'w']
        for init in initials_list:
            if pinyin.startswith(init):
                return init, pinyin[len(init):]
        return "", pinyin

    def _align_and_analyze(self, ref_syllables: List[Dict], trans_syllables: List[Dict]) -> List[Dict]:
        """
        Align syllables and analyze errors.
        """
        # Dùng SequenceMatcher để align dựa trên pinyin base (không thanh điệu)
        ref_bases = [s['base'] for s in ref_syllables]
        trans_bases = [s['base'] for s in trans_syllables]

        matcher = SequenceMatcher(None, ref_bases, trans_bases)

        details = []
        ref_idx = 0
        trans_idx = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # So sánh chi tiết từng âm tiết
                for k in range(i2 - i1):
                    ref_s = ref_syllables[i1 + k]
                    trans_s = trans_syllables[j1 + k]
                    errors = self._compare_syllable(ref_s, trans_s)
                    details.append({
                        "pos": ref_idx,
                        "ref_char": ref_s.get('char', ''),
                        "trans_char": trans_s.get('char', ''),
                        "ref_pinyin": ref_s['pinyin'],
                        "trans_pinyin": trans_s['pinyin'],
                        "error_type": "correct" if not errors else "substitution",
                        "errors": errors
                    })
                    ref_idx += 1
                    trans_idx += 1

            elif tag == 'delete':
                for k in range(i2 - i1):
                    ref_s = ref_syllables[i1 + k]
                    details.append({
                        "pos": ref_idx,
                        "ref_char": ref_s.get('char', ''),
                        "trans_char": None,
                        "ref_pinyin": ref_s['pinyin'],
                        "trans_pinyin": None,
                        "error_type": "deletion",
                        "errors": ["missing_syllable"]
                    })
                    ref_idx += 1

            elif tag == 'insert':
                for k in range(j2 - j1):
                    trans_s = trans_syllables[j1 + k]
                    details.append({
                        "pos": ref_idx,
                        "ref_char": None,
                        "trans_char": trans_s.get('char', ''),
                        "ref_pinyin": None,
                        "trans_pinyin": trans_s['pinyin'],
                        "error_type": "insertion",
                        "errors": ["extra_syllable"]
                    })
                    trans_idx += 1

            elif tag == 'replace':
                # Xử lý replace: so sánh từng cặp
                for k in range(max(i2 - i1, j2 - j1)):
                    ref_s = ref_syllables[i1 + k] if i1 + k < i2 else None
                    trans_s = trans_syllables[j1 + k] if j1 + k < j2 else None
                    if ref_s and trans_s:
                        errors = self._compare_syllable(ref_s, trans_s)
                        details.append({
                            "pos": ref_idx,
                            "ref_char": ref_s.get('char', ''),
                            "trans_char": trans_s.get('char', ''),
                            "ref_pinyin": ref_s['pinyin'],
                            "trans_pinyin": trans_s['pinyin'],
                            "error_type": "substitution" if errors else "correct",
                            "errors": errors
                        })
                    elif ref_s:
                        details.append({
                            "pos": ref_idx,
                            "ref_char": ref_s.get('char', ''),
                            "trans_char": None,
                            "ref_pinyin": ref_s['pinyin'],
                            "trans_pinyin": None,
                            "error_type": "deletion",
                            "errors": ["missing_syllable"]
                        })
                    else:
                        details.append({
                            "pos": ref_idx,
                            "ref_char": None,
                            "trans_char": trans_s.get('char', '') if trans_s else None,
                            "ref_pinyin": None,
                            "trans_pinyin": trans_s['pinyin'] if trans_s else None,
                            "error_type": "insertion",
                            "errors": ["extra_syllable"]
                        })
                    ref_idx += 1
                    trans_idx += 1

        return details

    def _compare_syllable(self, ref: Dict, trans: Dict) -> List[str]:
        """
        So sánh hai âm tiết, trả về danh sách lỗi.
        """
        errors = []

        # So sánh phụ âm đầu
        if ref['initials'] != trans['initials']:
            errors.append(f"initials: {ref['initials']} → {trans['initials']}")

        # So sánh vần
        if ref['final'] != trans['final']:
            errors.append(f"final: {ref['final']} → {trans['final']}")

        # So sánh thanh điệu
        if ref['tone'] != trans['tone']:
            errors.append(f"tone: {ref['tone']} → {trans['tone']}")

        return errors

    def _generate_feedback(self, details: List[Dict], score: float) -> str:
        """
        Generate qualitative feedback based on error analysis.
        """
        total_errors = 0
        tone_errors = 0
        initials_errors = 0
        final_errors = 0
        missing = 0
        extra = 0

        for d in details:
            if d['error_type'] == 'deletion':
                missing += 1
                total_errors += 1
            elif d['error_type'] == 'insertion':
                extra += 1
                total_errors += 1
            elif d['error_type'] == 'substitution':
                for err in d.get('errors', []):
                    if 'tone' in err:
                        tone_errors += 1
                    elif 'initials' in err:
                        initials_errors += 1
                    elif 'final' in err:
                        final_errors += 1
                    total_errors += 1

        if total_errors == 0:
            return "Xuất sắc! Bạn đọc chính xác tất cả các âm tiết."

        feedback = f"Có {total_errors} lỗi phát âm: "
        if tone_errors:
            feedback += f"{tone_errors} lỗi thanh điệu, "
        if initials_errors:
            feedback += f"{initials_errors} lỗi phụ âm đầu, "
        if final_errors:
            feedback += f"{final_errors} lỗi vần, "
        if missing:
            feedback += f"{missing} lỗi thiếu âm tiết, "
        if extra:
            feedback += f"{extra} lỗi thừa âm tiết, "
        feedback = feedback.rstrip(", ")

        if score >= 90:
            feedback += ". Tuyệt vời! Chỉ còn một vài lỗi nhỏ."
        elif score >= 70:
            feedback += ". Tốt! Cần luyện thêm một số âm."
        else:
            feedback += ". Cần luyện tập nhiều hơn."

        return feedback