import os
import json
from openai import OpenAI


class DataParser:
    def __init__(self):
        # OpenAI API Key 설정
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def parsing_data(self, file_name):
        prefix = str(file_name).split("/")[-1].split("_")[0]
        file_nm = str(file_name).split("/")[-1].split(".")[0]
        output_path = f'quiz_json/{prefix}/{file_nm}.json'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # OCR에서 추출된 텍스트 로드
        with open(f'quiz_texts/{file_name}.txt', 'r', encoding='utf-8') as file:
            data = file.read()
            # OpenAI GPT-4 요청용 프롬프트 작성
            prompt = f"""
        Given the following plain text from an OCR extraction, please process the text to identify and extract all questions contained within. Each question should be structured into the following JSON format:
            {{"questions":[
                {{
                    "subject": "<subject_name>",  // Select one subject from the following: 스포츠사회학, 스포츠교육학, 스포츠심리학, 한국체육사, 운동생리학, 운동역학, 스포츠윤리
                    "topic": "<topic_name>",  // Extract the topic based on the context of the question
                    "sub_topic": "<sub_topic_name>",  // Generate a sub_topic based on the content or field of study related to the question
                    "question_text": "<question_text>",  // Extract the full question text as it appears in the OCR data
                    "example": [
                        "<example_text>"
                    ],  // Extract example if `<보기>` or any further description exists in the question, otherwise set this as `null`
                    "options": {{
                        "1": "<option1>",
                        "2": "<option2>",
                        "3": "<option3>",
                        "4": "<option4>"
                    }},
                    "correct_option": <correct_option_number>,  // Generate the correct option number based on the context of the question
                    "description": "<description>"  // Provide additional information or explanations in Korean based on the context of the question
                }},
                {{
                    <other question text>
                }}
            ]}}
        Text Input:
        {data}
        Instructions:
        
        Carefully extract every question from the given text input. The text file may contain multiple questions.
        For each question:
        Extract and fill in the subject, topic, and sub_topic fields based on the question's context.
        Include the full question_text and divide any examples or descriptive information (such as <보기>) into the example field.
        Ensure the options field contains valid multiple-choice options.
        Determine the correct_option based on context or available information in the text.
        Provide additional explanations or context in the description field.
        Use Korean symbols (㉠, ㉡, ㉢, ㉣, etc.) for the options if other symbols or numbers are present.
        Structure each extracted question as a separate JSON object.
        Combine all question objects into a single JSON array.
        Ensure the output is valid JSON and adheres strictly to the format specified above.
        Output Requirements:
        
        The output should be a JSON array containing all extracted and structured questions.
        Ensure every question is complete, correctly formatted, and contains all relevant fields."""

        # OpenAI API 호출
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts and structures quiz questions."
                                              "and Filled the empty space with your knowledge about the sports science except option"},
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
