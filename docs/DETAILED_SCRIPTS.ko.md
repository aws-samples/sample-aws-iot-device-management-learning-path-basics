# 상세 스크립트 문서

이 문서는 AWS IoT Device Management 프로젝트의 각 스크립트에 대한 포괄적인 정보를 제공합니다. 모든 스크립트는 최적의 성능과 안정성을 위해 네이티브 AWS SDK(boto3)를 사용합니다.

## 핵심 스크립트

### scripts/provision_script.py
**목적**: 네이티브 boto3 API를 사용한 디바이스 관리 시나리오를 위한 완전한 AWS IoT 인프라 프로비저닝.

**기능**:
- 검색 가능한 속성(customerId, country, manufacturingDate)을 가진 사물 유형 생성
- VIN 스타일 명명(Vehicle-VIN-001)으로 수천 개의 IoT 디바이스 프로비저닝
- 펌웨어 패키지용 버전 관리가 포함된 Amazon S3 스토리지 설정
- 여러 버전의 AWS IoT 소프트웨어 패키지 생성
- 디바이스 쿼리를 위한 AWS IoT Fleet Indexing 구성
- 안전한 작업을 위한 AWS Identity and Access Management(IAM) 역할 설정
- 국가별 정적 사물 그룹 생성(Fleet 명명 규칙)
- **병렬 처리**: 더 빠른 프로비저닝을 위한 동시 작업
- **향상된 오류 처리**: 강력한 boto3 예외 처리

**대화형 입력**:
1. 사물 유형(기본값: SedanVehicle,SUVVehicle,TruckVehicle)
2. 패키지 버전(기본값: 1.0.0,1.1.0)
3. 대륙 선택(1-7)
4. 국가(개수 또는 특정 코드)
5. 디바이스 수(기본값: 100)

**교육적 일시 중지**: IoT 개념을 설명하는 8개의 학습 순간

**속도 제한**: 지능형 AWS API 스로틀링(사물 80 TPS, 사물 유형 8 TPS)

**성능**: 디버그 모드가 아닐 때 병렬 실행, 디버그 모드에서는 깔끔한 출력을 위해 순차 실행

---

### scripts/cleanup_script.py
**목적**: 네이티브 boto3 API를 사용하여 지속적인 비용을 피하기 위한 AWS IoT 리소스의 안전한 제거.

**정리 옵션**:
1. **모든 리소스** - 완전한 인프라 정리
2. **사물만** - 디바이스 제거하지만 인프라 유지
3. **사물 그룹만** - 그룹화 제거하지만 디바이스 유지

**기능**:
- **네이티브 boto3 구현**: CLI 종속성 없음, 더 나은 오류 처리
- 지능형 속도 제한을 가진 **병렬 처리**
- **향상된 S3 정리**: 페이지네이터를 사용한 적절한 버전 관리 객체 삭제
- 정적 그룹과 동적 그룹을 자동으로 구분
- 사물 유형 사용 중단 처리(5분 대기)
- 상태 모니터링과 함께 AWS IoT Jobs 취소 및 삭제
- 포괄적인 IAM 역할 및 정책 정리
- Fleet Indexing 구성 비활성화
- **Shadow 정리**: 클래식 및 $package shadow 모두 제거
- **주체 분리**: 인증서 및 정책을 적절하게 분리

**안전성**: 확인을 위해 "DELETE" 입력 필요

**성능**: AWS API 제한을 준수하는 병렬 실행(사물 80 TPS, 동적 그룹 4 TPS)

---

[Note: This is a partial translation. Full translation of all sections would continue in the same format, maintaining technical terms in English while translating explanatory text to Korean.]

