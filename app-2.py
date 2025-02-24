import requests
import json
import logging
import pandas as pd

# 로그 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("lean_canvas.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Streamlit 설치 확인
try:
    import streamlit as st
except ModuleNotFoundError:
    import subprocess
    subprocess.run(["pip", "install", "streamlit"], check=True)
    import streamlit as st

# 페이지 설정
st.set_page_config(page_title="Lean Canvas 자동 생성", layout="wide")
st.title("Lean Canvas 자동 작성 & 피드백 시스템")

# Ollama 또는 Llama 3.2 8B API 엔드포인트
API_URL = "http://localhost:11434/api/generate"  # 실제 서비스 환경에 맞게 변경 필요
MODEL_NAME = "llama3.1:latest"  # 사용 가능한 모델 이름으로 변경 필요

# Lean Canvas 입력 폼
st.header("📌 Lean Canvas 입력")
problem = st.text_area("1.문제 정의", "타겟 고객이 겪고 있는 핵심 문제를 입력하세요.", help="예: 기존 시장에서 해결되지 않는 주요 고객 문제를 설명하세요.")
solution = st.text_area("2.솔루션", "제안하는 해결책을 입력하세요.", help="예: 고객 문제를 해결하기 위한 제품 또는 서비스의 핵심 기능을 설명하세요.")
key_metrics = st.text_area("3.핵심 지표", "비즈니스 성과를 측정할 주요 지표를 입력하세요.", help="예: 매출 성장률, 사용자 유지율, 고객 획득 비용 등을 기재하세요.")
unique_value = st.text_area("4.경쟁력", "경쟁사와 차별화되는 핵심 가치를 입력하세요.", help="예: 경쟁사 대비 차별화되는 경쟁력을 설명하세요.")
unfair_advantage = st.text_area("5.차별점", "다른 경쟁사가 쉽게 모방할 수 없는 장점을 입력하세요.", help="예: 경쟁사와 차별화되는 요소를 설명하세요.")
customer_segment = st.text_area("6.고객 세그먼트", "타겟 고객층을 구체적으로 입력하세요.", help="예: 주 사용 고객의 연령, 직업, 관심사 등을 기재하세요.")
channels = st.text_area("7.채널", "고객에게 다가갈 방법(예: SNS, 광고, 파트너십 등)을 입력하세요.", help="예: 제품이나 서비스를 고객에게 알리고 판매하는 방법을 설명하세요.")
cost_structure = st.text_area("8.비용 구조", "운영에 필요한 주요 비용 항목을 입력하세요.", help="예: 개발 비용, 마케팅 비용, 운영 비용 등을 기재하세요.")
revenue_streams = st.text_area("9.수익 모델", "수익을 창출하는 방식(예: 구독료, 광고, 판매 등)을 입력하세요.", help="예: 제품 판매, 광고 수익, 구독 기반 모델 등의 수익 구조를 설명하세요.")

# AI 피드백 요청
if st.button("💡 AI 피드백 받기"):
    with st.spinner("AI가 피드백을 생성 중입니다..."):
        prompt_text = f"""
        당신은 Lean Canvas 전문가입니다. 사용자의 입력을 평가하고, 더 나은 제안을 제공해주고 각 섹션별 점수(1-10)와 개선할 수 있는 구체적인 피드백을 제공해주세요.
        평가 기준:
        - 문제 정의: 입력된 문제가 명확하고 현실적인가? 원인은 무엇인가? 부족한 점이 있다면 보완할 방법을 제안하세요.
        - 솔루션: 해결책이 효과적이며 실행 가능한가? 개선이 필요하다면 어떤 점을 수정해야 하는지 설명하세요.
        - 핵심 지표: 측정 가능한 목표가 적절한가? 부족하다면 추가할 KPI를 추천하세요.
        - 경쟁력: 차별성이 충분한가? 경쟁력 강화를 위한 추가적인 제안을 포함하세요.
        - 차별점: 경쟁자가 쉽게 모방할 수 없는 요소인가? 부족한 부분을 어떻게 보완할 수 있는지 설명하세요.
        - 고객 세그먼트: 타겟 고객이 충분히 구체적인가? 고객 페르소나를 설정하여 더 정교한 타겟팅이 되도록 한다. 추가할 세그먼트가 있다면 제안하세요.
        - 채널: 고객에게 접근하는 방법이 효과적인가? 더 나은 전략이 있다면 제안하세요.
        - 비용 구조: 주요 비용 요소가 현실적인가? 비용 절감 방안을 제안하세요.
        - 수익 모델: 수익 창출 방식이 타당한가? 추가적인 수익 기회를 분석하여 제안하세요.
        
        사용자 입력:
        문제 정의: {problem}
        솔루션: {solution}
        핵심 지표: {key_metrics}
        경쟁력: {unique_value}
        차별점: {unfair_advantage}
        고객 세그먼트: {customer_segment}
        채널: {channels}
        비용 구조: {cost_structure}
        수익 모델: {revenue_streams}
        """
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt_text,
            "stream": False
        }
        
        logger.info("API 요청 시작")
        logger.info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(API_URL, json=payload)
            response_data = response.json()
            feedback = response_data.get("response", "AI 피드백을 가져오는 데 실패했습니다.")
            scores = response_data.get("scores", {})
            
            # 평가 점수를 표 형태로 출력
            df = pd.DataFrame(list(scores.items()), columns=["항목", "점수(1-10)"])
            st.subheader("📊 평가 점수")
            st.dataframe(df)
            
        except Exception as e:
            feedback = f"오류 발생: {str(e)}"
            logger.error(feedback)
        
        st.subheader("🔍 AI 피드백")
        st.write(feedback)

st.sidebar.header("ℹ️ 서비스 소개")
st.sidebar.write("이 툴은 Phillip.Hong 에 의해 개발되었습니다.")
