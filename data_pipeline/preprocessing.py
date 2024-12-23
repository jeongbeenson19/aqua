import os
import json
import data_parser


# DataParser 객체 생성
parser = data_parser.DataParser()


def parsing_text(text_directory_path):
    # 디렉토리 내 모든 파일을 순회하면서 .txt 파일에 대해 parsing_data() 실행
    for file_name in os.listdir(text_directory_path):
        # 파일이 .txt로 끝나는 경우
        if file_name.endswith('.txt'):
            # 확장자를 제외한 파일명 추출
            base_file_name = os.path.splitext(file_name)[0]

            # 결과 출력 (선택 사항)
            print(f"Processed {file_name} successfully.")

            # 데이터 파싱 실행
            return parser.parsing_data(base_file_name)


def json_parser(json_directory_path):
    # 디렉토리 내 모든 파일을 순회하면서 .json 파일을 처리

    # JSON을 임시로 저장할 리스트
    all_data = []

    directory_size = len(os.listdir(json_directory_path))
    for idx in range(1, directory_size + 1):
        file_name = f'{directory_name}_{idx}.json'
        print(file_name)
        # 파일이 .json로 끝나는 경우
        if file_name.endswith('.json'):
            file_path = os.path.join(json_directory_path, file_name)

            # JSON 파일을 읽고 데이터를 임시 리스트에 저장
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                all_data.extend(data['questions'])  # 각 JSON 파일 내의 'questions' 필드를 리스트에 추가

    # 합쳐진 데이터를 하나의 JSON 파일로 저장
    output_path = f'quiz_json/merged_json_{directory_name}_1.json'
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump({"questions": all_data}, json_file, ensure_ascii=False, indent=4)

    print(f"All JSON data successfully merged and saved to {output_path}")

    return output_path


def split_and_map_json_with_type(input_file, output_dir, quiz_set_counter, quiz_id_counter, questions_per_file=20):
    # JSON 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    questions = data["questions"]
    total_questions = len(questions)
    total_files = (total_questions + questions_per_file - 1) // questions_per_file  # 필요한 파일 수 계산

    # quiz_type 리스트
    quiz_types = ["SCT", "EDU", "PSY", "HIS", "PHY", "KIN", "ETH"]

    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    # 퀴즈 ID 및 세트 ID 할당
    for set_index in range(total_files):
        start = set_index * questions_per_file
        end = start + questions_per_file
        subset = questions[start:end]

        quiz_type = quiz_types[set_index % len(quiz_types)]  # 순환적으로 quiz_type 할당
        quiz_set_id = f"quiz_set_{quiz_set_counter}"  # quiz_set_id 고정
        output_data = {
            "quiz_type": quiz_type,
            "quiz_set_id": quiz_set_id,
            "quiz": []
        }

        for question in subset:
            output_data["quiz"].append({
                "quiz_id": f"quiz_{quiz_id_counter}",
                "quiz_content": question
            })
            quiz_id_counter += 1

        # 파일 저장
        output_file = os.path.join(output_dir, f"{quiz_type}_{quiz_set_id}.json")
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(output_data, outfile, ensure_ascii=False, indent=4)

    print(f"Successfully split and saved {total_files} files in {output_dir}.")


directory_name = "2023A"
# 디렉토리 내 모든 .txt 파일 찾기
text_directory_path = f'quiz_texts/{directory_name}'  # quiz_texts 디렉토리로 설정
# 디렉토리 내 모든 .json 파일 찾기
json_directory_path = f'quiz_json/{directory_name}'  # JSON 파일이 저장된 디렉토리 경로

parsing_text(text_directory_path)
input_file = json_parser(json_directory_path)
output_dir = "quiz_json"  # 출력 디렉토리
split_and_map_json_with_type(input_file, output_dir, 1, 1)



