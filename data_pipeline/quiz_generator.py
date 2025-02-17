import os
import json
from openai import OpenAI


class QuizGenerator:
    def __init__(self):
        # OpenAI API Key 설정
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.topic = {
            "sct": ["스포츠사회학의 이해", "스포츠와 정치", "스포츠와 경제", "스포츠와 교육", "스포츠와 미디어", "스포츠와 사회계급/계층", "스포츠와 사회화", "스포츠와 일탈", "미래사회의 스포츠"],
            "edu": ["배경과 개념", "정책과 제도", "참여자 이해론", "프로그램론", "지도방법론", "평가론", "교육자의 전문적 성장"],
            "psy": ["스포츠심리학의 개관", "인간운동행동의 이해", "스포츠수행의 심리적 요인", "스포츠수행의 사회 심리적 요인", "운동심리학", "스포츠심리상담"],
            "his": ["체육사의 의미", "선사·삼국시대", "고려·조선시대", "한국 근·현대"],
            "phy": ["운동생리학의 개관", "에너지 대사", "신경조절", "골격근", "내분비계", "호흡·순환계", "환경과 운동"],
            "kin": ["운동역학 개요", "인체역학", "운동학의 적용", "운동역학의 적용", "일과 에너지", "운동기술의 분석"],
            "eth": ["스포츠와 윤리", "경쟁과 페어플레이", "스포츠와 불평등", "스포츠에서 환경과 동물윤리", "스포츠와 폭력", "경기력 향상과 공정성", "스포츠와 인권", "스포츠조직과 윤리"]
        }

    def generating_quiz(self, file_name, quiz_id):
        subject = str(file_name).split(".")[0].split("_")[0]
        topic = self.topic[subject.lower()]
        quiz_set_counter = int(file_name.split(".")[0].split("_")[-1])
        output_path = f'quiz_json/{subject}_quiz_set_{quiz_set_counter + 1}.json'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # OCR에서 추출된 텍스트 로드
        with open(f'quiz_json/{file_name}.json', 'r', encoding='utf-8') as file:
            data = file.read()
            # OpenAI GPT-4 요청용 프롬프트 작성
            prompt = f"""
            input_json_file = {data}
            {{
            "quiz_type": "<quiz_type>", // same as data
            "quiz_set_id": "<quiz_set_id>", // data["quiz_set_id"] += 1
            "quiz": [
                {{
                    "quiz_id": "<quiz_id>", // "{{quiz_type}}_{quiz_id}", quiz_id += 1 until last quiz
                    "quiz_content": {{
                        "subject": "<subject>", // same as data
                        "topic": "<topic>", // {topic}, choose a topic according to question content,
                        "sub_topic": "<sub_topic>", // you can change with similar one,
                        "question_text": "<question_text>", // generate the question text for this quiz following the subject, topic and sub_topic
                        // Ensure that the generated content matches the tone, style, and structure of the provided data.
                        "example": [
                            <example_text>
                        ], // if you need further explanations for this quiz. you can generate the example text for this quiz but no necessary
                        "options": {{
                            "1": "<option_1>",,
                            "2": "<option_2>",
                            "3": "<option_3>",
                            "4": "<option_4>" // options' length should 4
                        }},
                        "correct_option": <correct_option>,
                        "description": "<description>" // explanation for this quiz's answer
                    }},
                    {{...}} // generate the 20 questions
                }},
            - Ensure that the questions are framed with technical language and specialized terms, suitable for an academic or expert-level audience. 
            """

        # OpenAI API 호출
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in sports science and physical education. When generating questions, use academic terminology instead of general terms. For example, use physical activity instead of exercise and prioritize academic definitions over simple explanations. Follow the prompt to create detailed quizzes."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        # 결과를 JSON으로 변환
        quiz_data = json.loads(response.choices[0].message.content)

        # 결과 저장
        with open(output_path, 'w', encoding='utf-8') as json_file:
            print("Quiz data successfully extracted and saved to 'quiz_json/quiz_output.json'")
            json.dump(quiz_data, json_file, ensure_ascii=False, indent=4)

        return quiz_data


generator = QuizGenerator()
generator.generating_quiz("PSY_quiz_set_3", 341)
