import os
import json
from openai import OpenAI


class QuizGenerator:
    def __init__(self):
        # OpenAI API Key 설정
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def generating_quiz(self, file_name, quiz_id):
        subject = str(file_name).split(".")[0].split("_")[0]
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
                    "quiz_id": "<quiz_id>", // "quiz_{quiz_id}", quiz_id += 1 until last quiz
                    "quiz_content": {{
                        "subject": "<subject>", // same as data
                        "topic": "<topic>", // same as data,
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
                {"role": "system", "content": "You are an AI assistant specializing in sports science quiz generation. Follow the prompt to create detailed quizzes."},
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
generator.generating_quiz("PSY_quiz_set_1", 201)
