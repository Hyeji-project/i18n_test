# i18n 비교 로직 수정 제안서

현재 `i18n_test.py`의 비교 로직은 플레이스홀더, 특수문자, 공백 처리에 있어 개선이 필요합니다. 아래는 이를 해결하기 위한 구체적인 수정 방안입니다.

## 1. 텍스트 정규화 (`normalize_text`) 수정

**목적**: 줄바꿈(`\n`), 탭 등 다양한 공백을 단일 공백으로 통일하여 비교 정확도 향상.

**수정 전**:
```python
text = re.sub(r"<br\s*/?>", " ", text)
text = text.replace("&nbsp;", " ")
text = re.sub(r"\s+", " ", text) # 단순히 공백을 줄이기만 함
```

**수정 후 (제안)**:
```python
def normalize_text(text: str) -> str:
    # ... (기존 null 체크)
    text = text.lower()
    text = re.sub(r"<br\s*/?>", " ", text)
    text = text.replace("&nbsp;", " ")
    
    # [핵심 변경] 모든 형태의 공백(줄바꿈 포함)을 스페이스 하나로 치환
    text = re.sub(r"\s+", " ", text) 
    
    return text.strip()
```

## 2. 비교 로직 (`compare_i18n`) 수정

**목적**: 정규표현식을 강화하여 플레이스홀더 불일치, 별표(`*`) 유무, 문장 부호 주변 공백 차이를 유연하게 허용.

**수정 전**:
- 단순 `re.escape` 사용
- 제한적인 플레이스홀더 처리 (`{MM-DD-YYYY}` 등 특정 패턴만 고려 가능성)
- 별표 제거 방식이 단순함

**수정 후 (제안)**:
```python
def compare_i18n(frd: str, api: str) -> str:
    # ... (기존 초기화)
    frd = normalize_text(frd)
    api = normalize_text(api)

    # 1. 기본 이스케이프
    pattern = re.escape(frd)

    # 2. [핵심] 플레이스홀더 유연화
    # {...} 형태는 내용 불문하고 무엇이든 매칭되도록 변경
    pattern = re.sub(r"\\\{.*?\\\}", r".*?", pattern)

    # 3. [핵심] 별표(*) 선택적 처리
    # 별표가 있어도 되고 없어도 되도록 패턴 변경
    pattern = pattern.replace(r"\*", r"(\s*\*)*")

    # 4. 문장 부호(:, ?, !, .) 앞뒤의 유연한 공백 처리
    for char in [r"\:", r"\?", r"\!", r"\."]:
        pattern = pattern.replace(char, rf"\s*{char}\s*")

    # 5. 일반 공백 유연화
    pattern = pattern.replace(r"\ ", r"\s*")

    # 6. 전체 매칭 (앞뒤 공백 무시)
    final_pattern = r"^\s*" + pattern + r"\s*$"

    return "PASS" if re.fullmatch(final_pattern, api, re.DOTALL) else "FAIL"
```

## 해결되는 케이스
- **플레이스홀더**: `Last checked : {MM-DD-YYYY}` vs `Last checked : {0}` (PASS)
- **실제 값**: `Last checked : {MM-DD-YYYY}` vs `Last checked: 01-28-2026` (PASS)
- **특수문자**: `Postcode *` vs `Postcode` (PASS)
- **줄바꿈**: `Hello\nWorld` vs `Hello World` (PASS)
