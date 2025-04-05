import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import re
import time
import os

load_dotenv()
API_KEY = os.getenv("NPS_API_KEY")
API_DELAY = 0.5  # API 호출 간 대기 시간

def find_consecutive_match(name1, name2, min_length=2):
    """
    두 문자열에서 연속된 부분 문자열 매칭 여부 확인
    min_length 이상의 연속된 문자가 매칭되면 True 반환
    """
    # 공백과 특수문자 제거, 소문자로 변환
    name1 = re.sub(r'[^\w\s]', '', name1.replace(" ", "").lower())
    name2 = re.sub(r'[^\w\s]', '', name2.replace(" ", "").lower())
    
    # 회사 형태 관련 문자열 제거 (주식회사, 주, (주) 등)
    name1 = re.sub(r'주식회사|(주)|주', '', name1)
    name2 = re.sub(r'주식회사|(주)|주', '', name2)
    
    print(f"정제된 회사명 비교: '{name1}' vs '{name2}'")
    
    # 최소 길이 이상의 연속된 부분 문자열 찾기
    for i in range(len(name1) - min_length + 1):
        substring = name1[i:i+min_length]
        if substring in name2:
            print(f"✅ 연속 매칭 발견: '{substring}'")
            return True
    
    print("❌ 연속 매칭 없음")
    return False

def get_detail_info(seq: str, data_crt_ym: str) -> str:
    url = 'http://apis.data.go.kr/B552015/NpsBplcInfoInqireService/getDetailInfoSearch'
    params = {
        'serviceKey': API_KEY,
        'seq': seq,
        'data_crt_ym': data_crt_ym
    }
    try:
        time.sleep(API_DELAY)
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"오류: 전체사원수 API 호출 실패 (상태 코드 {response.status_code})")
            return ""
        root = ET.fromstring(response.content)
        if root.findtext('.//resultCode') != '00':
            return ""
        jnngp_cnt = root.findtext('.//items/item/jnngpCnt')
        if jnngp_cnt is None:
            jnngp_cnt = root.findtext('.//body/item/jnngpCnt')
        if jnngp_cnt is None:
            jnngp_cnt = root.findtext('.//jnngpCnt')
        if not jnngp_cnt and '<jnngpCnt>' in response.text:
            jnngp_cnt_match = re.search(r'<jnngpCnt>(\d+)</jnngpCnt>', response.text)
            if jnngp_cnt_match:
                jnngp_cnt = jnngp_cnt_match.group(1)
        return jnngp_cnt or ""
    except Exception as e:
        print(f"오류: get_detail_info 예외 - {e}")
        return ""

def get_monthly_status_info(seq: str, data_crt_ym: str) -> dict:
    url = 'http://apis.data.go.kr/B552015/NpsBplcInfoInqireService/getPdAcctoSttusInfoSearch'
    params = {
        'serviceKey': API_KEY,
        'seq': seq,
        'data_crt_ym': data_crt_ym
    }
    try:
        time.sleep(API_DELAY)
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"오류: 월별 취업/퇴직자 API 호출 실패 (상태 코드 {response.status_code})")
            return {}
        root = ET.fromstring(response.content)
        if root.findtext('.//resultCode') != '00':
            return {}
        total_count = int(root.findtext('.//totalCount', '0'))
        if total_count == 0:
            return {}
        nw_acqzr_cnt = root.findtext('.//items/item/nwAcqzrCnt')
        lss_jnngp_cnt = root.findtext('.//items/item/lssJnngpCnt')
        if nw_acqzr_cnt is None:
            nw_acqzr_cnt = root.findtext('.//nwAcqzrCnt')
        if lss_jnngp_cnt is None:
            lss_jnngp_cnt = root.findtext('.//lssJnngpCnt')
        if not (nw_acqzr_cnt or lss_jnngp_cnt):
            if '<nwAcqzrCnt>' in response.text:
                nw_match = re.search(r'<nwAcqzrCnt>(\d+)</nwAcqzrCnt>', response.text)
                if nw_match:
                    nw_acqzr_cnt = nw_match.group(1)
            if '<lssJnngpCnt>' in response.text:
                lss_match = re.search(r'<lssJnngpCnt>(\d+)</lssJnngpCnt>', response.text)
                if lss_match:
                    lss_jnngp_cnt = lss_match.group(1)
        return {
            'nwAcqzrCnt': nw_acqzr_cnt or '',
            'lssJnngpCnt': lss_jnngp_cnt or ''
        }
    except Exception as e:
        print(f"오류: get_monthly_status_info 예외 - {e}")
        return {}

def get_base_info(bz_number: str, data_crt_ym: str, company_name: str) -> list:
    url = 'http://apis.data.go.kr/B552015/NpsBplcInfoInqireService/getBassInfoSearch'
    results = []
    page_no = 1
    
    print(f"\n🔍 조회 시작: 사업자번호={bz_number[:6]}, 회사명={company_name}")
    
    while True:
        params = {
            'serviceKey': API_KEY,
            'bzowr_rgst_no': bz_number[:6],
            'data_crt_ym': data_crt_ym,
            'numOfRows': 100,
            'pageNo': page_no
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"오류: API 호출 실패 (상태 코드 {response.status_code})")
                break
            root = ET.fromstring(response.content)
            if root.findtext('.//resultCode') != '00':
                break
            items = root.findall('.//item')
        except Exception as e:
            print(f"오류: API 호출 예외 - {e}")
            break

        if not items:
            break
            
        print(f"🔍 {len(items)}개 사업장 검색 결과")

        for idx, item in enumerate(items):
            wkplNm = item.findtext('wkplNm', '')
            bzowrRgstNo = item.findtext('bzowrRgstNo', '')
            dataCrtYm = item.findtext('dataCrtYm', '')
            seq = item.findtext('seq', '')
            
            # 1. 사업자번호 앞 6자리 일치 확인
            if not bzowrRgstNo.startswith(bz_number[:6]):
                continue
                
            # 2. 회사명 연속 2글자 이상 매칭 확인 (추가된 부분)
            name_match = find_consecutive_match(company_name, wkplNm, min_length=2)
            
            print(f"[{idx}] {bzowrRgstNo} - {wkplNm} | 번호 매칭: O, 이름 매칭: {'O' if name_match else 'X'}")
            
            # 두 조건 모두 만족할 때만 상세 정보 조회
            if name_match:
                print(f"✅ 사업장 매칭 성공: {bzowrRgstNo} - {wkplNm}")

                if seq and dataCrtYm:
                    # 전체사원수 조회
                    jnngp_cnt = get_detail_info(seq, dataCrtYm)
                    
                    # 월별 취업/퇴직자 정보 조회
                    monthly_status = get_monthly_status_info(seq, dataCrtYm)
                    nw_acqzr_cnt = monthly_status.get('nwAcqzrCnt', '')
                    lss_jnngp_cnt = monthly_status.get('lssJnngpCnt', '')
                    
                    print(f"전체 정보 저장 완료: 전체사원수={jnngp_cnt}, 취업자수={nw_acqzr_cnt}, 퇴직자수={lss_jnngp_cnt}")
                    
                    # 모든 정보 저장
                    results.append({
                        '자료생성년월': dataCrtYm,
                        '사업자등록번호': bzowrRgstNo,
                        '사업장명': wkplNm,
                        '전체사원수': jnngp_cnt,
                        '월별 취업자수': nw_acqzr_cnt,
                        '월별 퇴직자수': lss_jnngp_cnt
                    })
                else:
                    print("seq 또는 dataCrtYm 값이 없음")
                    results.append({
                        '자료생성년월': dataCrtYm,
                        '사업자등록번호': bzowrRgstNo,
                        '사업장명': wkplNm,
                        '전체사원수': 'ERROR-NO-SEQ',
                        '월별 취업자수': 'ERROR-NO-SEQ',
                        '월별 퇴직자수': 'ERROR-NO-SEQ'
                    })
            else:
                print(f"❌ 사업장 매칭 실패: {bzowrRgstNo} - {wkplNm} (이름 매칭 안됨)")
                
        # 다음 페이지 여부 확인
        if len(items) < 100:
            break
        page_no += 1
        print(f"다음 페이지 조회: {page_no}")

    print(f"🔍 조회 완료: {len(results)}개 결과")
    return results