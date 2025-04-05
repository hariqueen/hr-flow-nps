import os
import time
import csv
from datetime import datetime
from api.nps_api import get_base_info
from utils.file_handler import load_business_data

# main.py가 위치한 디렉토리 내의 "output" 폴더로 출력 경로 설정
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
CSV_FILENAME = "국민연금사업장결과.csv"

def append_to_csv(row, output_dir, filename):
    """단일 행을 CSV에 추가"""
    try:
        # 출력 디렉토리 확인 및 생성
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"디렉토리 생성: {output_dir}")
            
        filepath = os.path.join(output_dir, filename)
        file_exists = os.path.exists(filepath)
        
        headers = ["자료생성년월", "사업자등록번호", "사업장명", "전체사원수", "월별 취업자수", "월별 퇴직자수"]
        
        # 파일 존재 여부에 따라 처리
        if not file_exists:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerow(row)
                print(f"새 파일 생성 및 데이터 저장: {row['사업장명']}")
        else:
            with open(filepath, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writerow(row)
                print(f"기존 파일에 데이터 추가: {row['사업장명']}")
                
        return True
            
    except Exception as e:
        print(f"CSV 저장 중 오류 발생: {e}")
        return False

def main():
    """메인 프로그램"""
    print("\n=== 국민연금 사업장 정보 수집 시작 ===\n")
    start_time = time.time()
    
    # 설정 정보 출력
    print(f"작업 디렉토리: {os.getcwd()}")
    print(f"출력 디렉토리: {OUTPUT_DIR}")
    
    # JSON 파일 확인
    json_path = "business_name.json"
    if not os.path.exists(json_path):
        print(f"오류: {json_path} 파일이 없습니다.")
        return
    
    # 비즈니스 데이터 로드
    try:
        biz_data = load_business_data(json_path)
        print(f"비즈니스 데이터 로드 완료: {len(biz_data)}개 기업")
    except Exception as e:
        print(f"비즈니스 데이터 로드 실패: {e}")
        return
    
    # 현재 년월 설정
    now = datetime.now()
    current_ym = now.strftime("%Y%m")
    print(f"조회 기준 년월: {current_ym}")
    
    # 처리 결과 통계
    total_companies = len(biz_data)
    success_count = 0
    failed_count = 0
    total_results = 0
    
    # CSV 파일 경로 확인
    output_filepath = os.path.join(OUTPUT_DIR, CSV_FILENAME)
    print(f"출력 파일: {output_filepath}")
    
    # 기업별 처리
    for i, company in enumerate(biz_data):
        company_idx = i + 1
        name = company['name']
        num = company['num']
        
        print(f"\n{'='*60}")
        print(f"[{company_idx}/{total_companies}] 기업 조회: {name} (번호: {num})")
        print(f"{'='*60}")
        
        # 데이터 조회
        results = get_base_info(num, current_ym, name)
        
        # 결과 처리
        if results:
            success_count += 1
            total_results += len(results)
            
            # 결과 저장
            for result in results:
                if append_to_csv(result, OUTPUT_DIR, CSV_FILENAME):
                    print(f"결과 저장 완료: {result['사업장명']}")
                else:
                    print(f"결과 저장 실패: {result['사업장명']}")
        else:
            failed_count += 1
            print(f"결과 없음: {name}")
        
        # 진행 상황 출력
        print(f"\n진행 상황: {company_idx}/{total_companies} "
              f"(성공: {success_count}, 실패: {failed_count}, 총 결과: {total_results})")
        
        # 마지막 기업이 아니면 대기
        if company_idx < total_companies:
            wait_time = 1  # 기업 간 대기 시간 (초)
            print(f"다음 기업 처리 전 {wait_time}초 대기...")
            time.sleep(wait_time)
    
    # 최종 요약
    elapsed_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"수집 결과 요약:")
    print(f"  - 총 기업 수: {total_companies}개")
    print(f"  - 성공한 기업 수: {success_count}개")
    print(f"  - 실패한 기업 수: {failed_count}개")
    print(f"  - 수집된 총 항목 수: {total_results}개")
    print(f"  - 저장 파일: {output_filepath}")
    print(f"  - 총 소요 시간: {elapsed_time:.2f}초 ({elapsed_time/60:.2f}분)")
    print(f"{'='*60}\n")
    
    print("국민연금 사업장 정보 수집 완료")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"\n프로그램 실행 중 오류 발생: {e}")
        print(traceback.format_exc())
    finally:
        print("\n프로그램 종료. Enter 키를 눌러 창을 닫으세요...")
        input()