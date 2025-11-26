# 사용 예제

이 문서는 AWS IoT Device Management의 일반적인 시나리오에 대한 실용적인 예제를 제공합니다.

## 빠른 시작 예제

### 기본 플릿 설정
```bash
# 1. 인프라 생성
python scripts/provision_script.py
# 선택: SedanVehicle,SUVVehicle
# 버전: 1.0.0,1.1.0
# 지역: North America
# 국가: US,CA
# 디바이스: 100

# 2. 동적 그룹 생성
python scripts/manage_dynamic_groups.py
# 작업: 1 (생성)
# 국가: US
# 사물 유형: SedanVehicle
# 배터리 레벨: <30

# 3. 펌웨어 업데이트 작업 생성
python scripts/create_job.py
# 선택: USFleet 그룹
# 패키지: SedanVehicle v1.1.0

# 4. 디바이스 업데이트 시뮬레이션
python scripts/simulate_job_execution.py
# 성공률: 85%
# 처리: 모든 실행
```

### 버전 롤백 시나리오
```bash
# 모든 SedanVehicle 디바이스를 버전 1.0.0으로 롤백
python scripts/manage_packages.py
# 선택: 10. 디바이스 버전 되돌리기
# 사물 유형: SedanVehicle
# 대상 버전: 1.0.0
# 확인: REVERT
```

### 작업 모니터링
```bash
# 작업 진행 상황 모니터링
python scripts/explore_jobs.py
# 옵션 1: 모든 작업 나열
# 옵션 4: 특정 작업에 대한 작업 실행 나열
```

## 고급 시나리오

### 다중 리전 배포
```bash
# 여러 리전에서 프로비저닝
export AWS_DEFAULT_REGION=us-east-1
python scripts/provision_script.py
# 북미에 500개 디바이스 생성

export AWS_DEFAULT_REGION=eu-west-1  
python scripts/provision_script.py
# 유럽에 300개 디바이스 생성
```

### 단계적 롤아웃
```bash
# 1. 테스트 그룹 생성
python scripts/manage_dynamic_groups.py
# 작업: 1 (생성)
# 국가: US
# 사물 유형: SedanVehicle
# 버전: 1.0.0
# 사용자 정의 이름: TestFleet_SedanVehicle_US

# 2. 먼저 테스트 그룹에 배포
python scripts/create_job.py
# 선택: TestFleet_SedanVehicle_US
# 패키지: SedanVehicle v1.1.0

# 3. 테스트 배포 모니터링
python scripts/simulate_job_execution.py
# 성공률: 95%

# 4. 검증 후 프로덕션에 배포
python scripts/create_job.py
# 선택: USFleet
# 패키지: SedanVehicle v1.1.0
```

### 배터리 기반 유지보수
```bash
# 낮은 배터리 그룹 생성
python scripts/manage_dynamic_groups.py
# 작업: 1 (생성)
# 방법: 1 (가이드 마법사)
# 국가: (모두의 경우 비워둠)
# 사물 유형: (모두의 경우 비워둠)
# 배터리 레벨: <20
# 사용자 정의 이름: LowBatteryDevices

# 유지보수 작업 생성
python scripts/create_job.py
# 선택: LowBatteryDevices
# 패키지: MaintenanceFirmware v2.0.0
```

### 고급 사용자 정의 쿼리
```bash
# 사용자 정의 쿼리로 복잡한 그룹 생성
python scripts/manage_dynamic_groups.py
# 작업: 1 (생성)
# 방법: 2 (사용자 정의 쿼리)
# 쿼리: (thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]
# 그룹 이름: USVehicles_MidBattery
```

### 패키지 관리
```bash
# 새 패키지 및 버전 생성
python scripts/manage_packages.py
# 작업: 1 (패키지 생성)
# 패키지 이름: TestVehicle

# S3 업로드로 버전 추가
# 작업: 2 (버전 생성)
# 패키지 이름: TestVehicle
# 버전: 2.0.0

# 패키지 세부 정보 검사
# 작업: 4 (패키지 설명)
# 패키지 이름: TestVehicle
```

## 개발 워크플로

### 새 펌웨어 테스트
```bash
# 1. 테스트 환경 프로비저닝
python scripts/provision_script.py
# 사물 유형: TestSensor
# 버전: 1.0.0,2.0.0-beta
# 국가: US
# 디바이스: 10

# 2. 베타 테스트 그룹 생성
python scripts/manage_dynamic_groups.py
# 작업: 1 (생성)
# 사물 유형: TestSensor
# 버전: 1.0.0
# 사용자 정의 이름: BetaTestGroup

# 3. 베타 펌웨어 배포
python scripts/create_job.py
# 선택: BetaTestGroup
# 패키지: TestSensor v2.0.0-beta

# 4. 테스트를 위해 높은 실패율로 시뮬레이션
python scripts/simulate_job_execution.py
# 성공률: 60%

# 5. 결과 분석
python scripts/explore_jobs.py
# 옵션 4: 작업 실행 나열
```

### 테스트 후 정리
```bash
# 테스트 리소스 정리
python scripts/cleanup_script.py
# 옵션 1: 모든 리소스
# 확인: DELETE
```

## 플릿 관리 패턴

### 지리적 배포
```bash
# 대륙별 프로비저닝
python scripts/provision_script.py
# 대륙: 1 (북미)
# 국가: 3 (처음 3개 국가)
# 디바이스: 1000

# 국가별 그룹 생성 (USFleet, CAFleet, MXFleet로 자동 생성)
# 지역별 펌웨어 배포
python scripts/create_job.py
# 선택: USFleet,CAFleet
# 패키지: RegionalFirmware v1.2.0
```

### 디바이스 유형 관리
```bash
# 여러 차량 유형 프로비저닝
python scripts/provision_script.py
# 사물 유형: SedanVehicle,SUVVehicle,TruckVehicle
# 버전: 1.0.0,1.1.0,2.0.0
# 디바이스: 500

# 유형별 동적 그룹 생성
python scripts/manage_dynamic_groups.py
# 작업: 1 (생성)
# 사물 유형: TruckVehicle
# 국가: US,CA
# 사용자 정의 이름: NorthAmericaTrucks

# 트럭 전용 펌웨어 배포
python scripts/create_job.py
# 선택: NorthAmericaTrucks
# 패키지: TruckVehicle v2.0.0
```

### 유지보수 스케줄링
```bash
# 업데이트가 필요한 디바이스 찾기
python scripts/manage_dynamic_groups.py
# 작업: 1 (생성)
# 사물 유형: SedanVehicle
# 버전: 1.0.0  # 이전 버전
# 사용자 정의 이름: SedanVehicle_NeedsUpdate

# 유지보수 기간 배포 스케줄
python scripts/create_job.py
# 선택: SedanVehicle_NeedsUpdate
# 패키지: SedanVehicle v1.1.0

# 배포 진행 상황 모니터링
python scripts/explore_jobs.py
# 옵션 1: 모든 작업 나열 (상태 확인)
```

## 문제 해결 예제

### 실패한 작업 복구
```bash
# 1. 작업 상태 확인
python scripts/explore_jobs.py
# 옵션 2: 특정 작업 탐색
# 실패가 있는 작업 ID 입력

# 2. 개별 디바이스 실패 확인
python scripts/explore_jobs.py
# 옵션 3: 작업 실행 탐색
# 작업 ID 및 실패한 디바이스 이름 입력

# 3. 실패한 디바이스 롤백
python scripts/manage_packages.py
# 선택: 10. 디바이스 버전 되돌리기
# 사물 유형: SedanVehicle
# 대상 버전: 1.0.0  # 이전 작동 버전
```

### 디바이스 상태 확인
```bash
# 현재 펌웨어 버전 확인
python scripts/manage_dynamic_groups.py
# 작업: 1 (생성)
# 사물 유형: SedanVehicle
# 버전: 1.1.0
# 사용자 정의 이름: SedanVehicle_v1_1_0_Check

# 그룹 멤버십 확인 (예상 개수와 일치해야 함)
python scripts/explore_jobs.py
# 디바이스 상태 확인에 사용
```

### 성능 테스트
```bash
# 대량의 디바이스로 테스트
python scripts/provision_script.py
# 디바이스: 5000

# 작업 실행 성능 테스트
python scripts/simulate_job_execution.py
# 처리: 모두
# 성공률: 90%
# 실행 시간 및 TPS 모니터링
```

## 환경별 예제

### 개발 환경
```bash
# 개발용 소규모
python scripts/provision_script.py
# 사물 유형: DevSensor
# 버전: 1.0.0-dev
# 국가: US
# 디바이스: 5
```

### 스테이징 환경
```bash
# 스테이징용 중간 규모
python scripts/provision_script.py
# 사물 유형: SedanVehicle,SUVVehicle
# 버전: 1.0.0,1.1.0-rc
# 국가: US,CA
# 디바이스: 100
```

### 프로덕션 환경
```bash
# 프로덕션용 대규모
python scripts/provision_script.py
# 사물 유형: SedanVehicle,SUVVehicle,TruckVehicle
# 버전: 1.0.0,1.1.0,1.2.0
# 대륙: 1 (북미)
# 국가: 모두
# 디바이스: 10000
```

## 통합 예제

### CI/CD 파이프라인 통합
```bash
# 구문 검사 (자동화)
python scripts/check_syntax.py

# 자동화된 테스트
python scripts/provision_script.py --automated
python scripts/create_job.py --test-mode
python scripts/simulate_job_execution.py --success-rate 95
python scripts/cleanup_script.py --force
```

### 모니터링 통합
```bash
# 작업 메트릭 내보내기
python scripts/explore_jobs.py --export-json > job_status.json

# 배포 상태 확인
python scripts/explore_jobs.py --health-check
```

## 모범 사례 예제

### 점진적 롤아웃
1. 플릿의 5%로 시작 (테스트 그룹)
2. 24시간 동안 모니터링
3. 성공 시 25%로 확장
4. 검증 후 전체 배포

### 롤백 전략
1. 항상 롤백 절차 테스트
2. 이전 펌웨어 버전을 사용 가능하게 유지
3. 배포 후 디바이스 상태 모니터링
4. 자동 롤백 트리거 준비

### 리소스 관리
1. 테스트 후 정리 스크립트 사용
2. AWS 비용 모니터링
3. 이전 펌웨어 버전 정리
4. 사용하지 않는 사물 그룹 제거
