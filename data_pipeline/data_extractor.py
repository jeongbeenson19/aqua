import fitz  # PyMuPDF
from PIL import Image
from google.cloud import vision
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "dulcet-opus-443011-u1-dfe77b2064f0.json"


def pdf_to_images(pdf_path, output_folder, dpi=300):
    """
    PDF 파일을 이미지로 변환 및 저장
    """
    os.makedirs(os.path.dirname(output_folder), exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    file_nm = str(pdf_path).split("/")[-1].split(".")[0]

    for page_num in range(len(doc)):
        # 각 페이지를 이미지로 변환
        zoom = dpi / 72  # 기본 DPI는 72
        matrix = fitz.Matrix(zoom, zoom)
        pix = doc[page_num].get_pixmap(matrix=matrix)
        image_path = f"{output_folder}/{file_nm}_{page_num + 1}.png"
        pix.save(image_path)
        image_paths.append(image_path)

    return image_paths


def crop_image(image_path, coordinates, cropped_path):
    """
    이미지에서 특정 영역을 잘라내기
    coordinates: (x1, y1, x2, y2)
    """
    os.makedirs(os.path.dirname(cropped_path), exist_ok=True)

    with Image.open(image_path) as img:
        cropped_img = img.crop(coordinates)
        cropped_img.save(cropped_path)

        return cropped_path


def detect_text(image_path, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Vision API 클라이언트 초기화
    client = vision.ImageAnnotatorClient()

    # 이미지 파일 읽기
    with open(image_path, "rb") as image_file:
        content = image_file.read()

    # Vision API 요청 생성
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations[0].description

    # 결과 출력
    if texts:
        print("텍스트 감지 결과:")
        with open(output_path, "a", encoding="utf-8") as output_file:  # 'a' 모드로 파일을 열어 내용을 추가
            output_file.write(f"'{texts}'\n")  # 파일에 텍스트 추가
    else:
        print("텍스트를 감지하지 못했습니다.")

    # 에러 처리
    if response.error.message:
        raise Exception(f"API Error: {response.error.message}")


# PDF 슬라이싱 및 OCR 수행
pdf_path = "quiz_pdf/2023A.pdf"
doc_nm = str(pdf_path).split("/")[-1].split(".")[0]
output_folder = f"quiz_image/{doc_nm}"

coordinates_l = (0, 270, 1500, 4040)
coordinates_r = (1550, 270, 3000, 4040)

# 1. PDF를 이미지로 변환
images = pdf_to_images(pdf_path, output_folder)

# 2. 특정 영역 잘라내기 (슬라이싱)
for idx, image in enumerate(images[1:]):
    cropped_image_path_l = crop_image(image, coordinates_l,
                                      f"quiz_image_cropped/{doc_nm}/crpd_image{idx + 1}_l.png")

    detect_text(cropped_image_path_l, f"quiz_texts/{doc_nm}/{doc_nm}_{idx + 1}.txt")

    cropped_image_path_r = crop_image(image, coordinates_r,
                                      f"quiz_image_cropped/{doc_nm}/crpd_image{idx + 1}_r.png")

    detect_text(cropped_image_path_r, f"quiz_texts/{doc_nm}/{doc_nm}_{idx + 1}.txt")
