import json
import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# MongoDB 설정
password = os.environ.get('MONGO_PW')
password = quote_plus(password)

MONGO_URI = f"mongodb+srv://jeongbeenson19:{password}@aqua.wchta.mongodb.net/?retryWrites=true&w=majority&appName=aqua"
mongo_client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)

mongo_db = mongo_client['quiz_db']

subject = {
    "EDU": "스포츠교육학",
    "ETH": "스포츠윤리",
    "HIS": "한국체육사",
    "KIN": "운동역학",
    "PHY": "운동생리학",
    "PSY": "스포츠심리학",
    "SCT": "스포츠사회학"
}

topic = {
    "EDU": ["배경과 개념", "정책과 제도", "참여자 이해론", "프로그램론", "지도 방법론", "평가론", "교육자의 전문적 성장"],
    "ETH": ["스포츠와 윤리", "경쟁과 페어플레이", "스포츠와 불평등", "환경과 동물 윤리", "스포츠와 폭력", "경기력 향상과 공정성", "스포츠와 인권", "스포츠 조직과 윤리"],
    "HIS": ["체육사의 의미", "선사·삼국시대의 체육", "고려시대의 체육", "조선시대의 체육", "개화기의 체육", "일제 강점기의 체육", "광복 이후의 체육"],
    "PHY": ["운동생리학의 개관", "에너지 대사와 활동", "신경 조절과 운동", "골격근과 운동", "내분비계와 운동", "호흡·순환계와 운동", "환경과 운동"],
    "KIN": ["운동역학 개요", "운동역학의 이해", "인체 역학", "운동학의 스포츠 적용", "운동역학의 스포츠 적용", "일과 에너지", "운동 기술의 분석"],
    "PSY": ["스포츠심리학의 개관", "인간 운동 행동의 이해", "스포츠 수행의 심리적 요인", "스포츠 수행의 사회 심리적 요인", "건강 운동 심리학", "스포츠 심리 상담"],
    "SCT": ["스포츠사회학의 이해", "스포츠와 정치", "스포츠와 경제", "스포츠와 교육", "스포츠와 미디어", "스포츠와 사회계급/계층", "스포츠와 사회화", "스포츠와 일탈", "미래 사회의 스포츠"]
}


def check_quiz_set(quiz_set):
    quiz_type = quiz_set.split(".")[0].split("_")[0]

    print(f"🔹 quiz_set: {quiz_set}")
    print(f"🔹 quiz_type: {quiz_type}")

    if quiz_type not in subject:
        raise KeyError(f"❌ {quiz_type} 키가 subject 딕셔너리에 없습니다.")

    if quiz_type not in topic:
        raise KeyError(f"❌ {quiz_type} 키가 topic 딕셔너리에 없습니다.")

    file_path = f"quiz_json/generated_quiz_json/{quiz_set}.json"
    print(f"📂 파일 경로: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ 파일이 존재하지 않습니다: {file_path}")

    # 파일을 읽기 모드로 열기
    with open(file_path, "r", encoding="utf-8") as f:
        quiz_json = json.load(f)  # 파일 내용 읽기

    offer_file_path = f"quiz_json/{quiz_type}_offer.json"
    with open(offer_file_path, "r", encoding="utf-8") as offer:
        offer_file = json.load(offer)

    for quiz in quiz_json["quiz"]:
        print(f"📝 quiz_id: {quiz.get('quiz_id', '없음')}")

        if "quiz_content" not in quiz:
            raise KeyError(f"❌ quiz_id {quiz.get('quiz_id', '없음')}에 quiz_content 키가 없습니다.")

        if "subject" not in quiz["quiz_content"]:
            raise KeyError(f"❌ quiz_id {quiz['quiz_id']}에 subject 키가 없습니다.")

        if "topic" not in quiz["quiz_content"]:
            raise KeyError(f"❌ quiz_id {quiz['quiz_id']}에 topic 키가 없습니다.")

        print(f"📚 현재 subject: {quiz['quiz_content']['subject']}, 기대값: {subject[quiz_type]}")

        if quiz["quiz_content"]["subject"] != subject[quiz_type]:
            print(f"⚠️ subject 수정: {quiz['quiz_content']['subject']} -> {subject[quiz_type]}")
            quiz["quiz_content"]["subject"] = subject[quiz_type]

        print(f"📌 현재 topic: {quiz['quiz_content']['topic']}, 기대값 리스트: {topic[quiz_type]}")

        quiz_id_int = int(quiz["quiz_id"].split("_")[-1])

        topic_in_offer = offer_file["quiz"][(quiz_id_int - 1) % 20]["quiz_content"]["topic"]
        if quiz["quiz_content"]["topic"] != topic_in_offer:
            print(f"⚠️ topic 수정: {quiz['quiz_content']['topic']} -> {topic_in_offer}")
            quiz["quiz_content"]["topic"] = topic_in_offer

    # 수정된 quiz_json을 파일에 저장
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(quiz_json, f, ensure_ascii=False, indent=4)


def upload_quiz(quiz_set):
    """
    quiz_type에 해당하는 컬렉션에 quiz_data를 업로드하는 함수
    """
    check_quiz_set(quiz_set)
    quiz_type = quiz_set.split(".")[0].split("_")[0]
    collection_name = quiz_type.lower()  # 컬렉션 이름을 소문자로 변환
    collection = mongo_db[collection_name]  # 해당하는 컬렉션 선택

    # JSON 파일을 읽어와야 함
    file_path = f"quiz_json/generated_quiz_json/{quiz_set}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        quiz_data = json.load(f)  # 파일 내용 읽기

    # MongoDB에 삽입
    result = collection.insert_one(quiz_data)
    print(result.inserted_id)  # 삽입된 문서의 ID 반환


upload_quiz("SCT_4")
