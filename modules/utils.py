"""
공통 유틸리티 모듈 - 날짜 계산, 포맷 변환 등 공용 함수 모음
"""
from datetime import datetime, timedelta


def today_str(fmt: str = "%Y-%m-%d") -> str:
    """오늘 날짜를 문자열로 반환합니다."""
    return datetime.now().strftime(fmt)


def add_days(base_date: str, days: int, fmt: str = "%Y-%m-%d") -> str:
    """기준일로부터 N일 후 날짜를 반환합니다."""
    base = datetime.strptime(base_date, fmt)
    return (base + timedelta(days=days)).strftime(fmt)


def format_phone(phone: str) -> str:
    """전화번호를 하이픈 포함 형태로 변환합니다. 예: 01012345678 -> 010-1234-5678"""
    digits = phone.replace("-", "").replace(" ", "")
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    return phone
