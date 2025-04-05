import os
import csv

test_data = {
    '자료생성년월': '202504',
    '사업자등록번호': '1208173505',
    '사업장명': '테스트회사',
    '전체사원수': '10',
    '월별 취업자수': '2',
    '월별 퇴직자수': '1'
}

output_dir = r"G:\내 드라이브\업무용\Meta M\job\output"
filename = "테스트저장.csv"
filepath = os.path.join(output_dir, filename)

print(f"파일 저장 시작: {filepath}")

headers = ["자료생성년월", "사업자등록번호", "사업장명", "전체사원수", "월별 취업자수", "월별 퇴직자수"]

with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerow(test_data)
    print("저장 완료")

print(f"파일 크기: {os.path.getsize(filepath)} 바이트")
print("저장 테스트 종료")