# AWS IoT Device Management - Learning Path - Basics

## 🌍 Available Languages | Idiomas Disponibles | 利用可能な言語 | 사용 가능한 언어 | Idiomas Disponíveis | 可用语言

| Language | README |
|----------|---------|
| 🇺🇸 English | [README.md](README.md) |
| 🇪🇸 Español | [README.es.md](README.es.md) |
| 🇯🇵 日本語 | [README.ja.md](README.ja.md) |
| 🇰🇷 한국어 | [README.ko.md](README.ko.md) |
| 🇧🇷 Português | [README.pt.md](README.pt.md) |
| 🇨🇳 中文 | [README.zh.md](README.zh.md) |

---

네이티브 AWS SDK (boto3) 통합을 사용하는 최신 Python 스크립트를 통해 디바이스 프로비저닝, 무선 업데이트(OTA), 작업 관리 및 플릿 운영을 포함한 AWS IoT Device Management 기능의 포괄적인 데모입니다.

## 👥 대상 사용자

**주요 대상:** AWS IoT 디바이스 플릿을 다루는 IoT 개발자, 솔루션 아키텍트, DevOps 엔지니어

**전제 조건:** 중급 AWS 지식, AWS IoT Core 기초, Python 기초, 명령줄 사용법

**학습 수준:** 대규모 디바이스 관리에 대한 실습 접근 방식의 어소시에이트 수준

## 🎯 학습 목표

- **디바이스 라이프사이클 관리**: 적절한 Thing 타입과 속성으로 IoT 디바이스 프로비저닝
- **플릿 조직**: 디바이스 관리를 위한 정적 및 동적 Thing 그룹 생성
- **OTA 업데이트**: Amazon S3 통합을 통한 AWS IoT Jobs를 사용한 펌웨어 업데이트 구현
- **패키지 관리**: 자동화된 섀도우 업데이트를 통한 다중 펌웨어 버전 처리
- **작업 실행**: 펌웨어 업데이트 중 현실적인 디바이스 동작 시뮬레이션
- **버전 제어**: 디바이스를 이전 펌웨어 버전으로 롤백
- **원격 명령**: AWS IoT Commands를 사용하여 디바이스에 실시간 명령 전송
- **리소스 정리**: 불필요한 비용을 피하기 위한 AWS 리소스 적절한 관리

## 📋 전제 조건

- AWS IoT, Amazon S3, AWS Identity and Access Management (IAM) 권한이 있는 **AWS 계정**
- 구성된 **AWS 자격 증명** (`aws configure`, 환경 변수 또는 AWS Identity and Access Management (IAM) 역할을 통해)
- pip와 boto3, colorama, requests Python 라이브러리가 포함된 **Python 3.10+** (requirements.txt 파일 확인)
- 저장소 복제를 위한 **Git**

## 💰 비용 분석

**이 프로젝트는 요금이 발생하는 실제 AWS 리소스를 생성합니다.**

| 서비스 | 사용량 | 예상 비용 (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~1,000개 메시지, 100-10,000개 디바이스 | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | ~200-2,000개 섀도우 작업 | $0.10 - $1.00 |
| **AWS IoT Jobs** | ~10-100개 작업 실행 | $0.01 - $0.10 |
| **AWS IoT Commands** | ~10-50개 명령 실행 | $0.01 - $0.05 |
| **Amazon S3** | 펌웨어용 스토리지 + 요청 | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | 디바이스 쿼리 및 인덱싱 | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | 패키지 작업 | $0.01 - $0.05 |
| **AWS Identity and Access Management (IAM)** | 역할/정책 관리 | $0.00 |
| **총 예상 비용** | **완전한 데모 세션** | **$0.28 - $2.45** |

**비용 요인:**
- 디바이스 수 (100-10,000 구성 가능)
- 작업 실행 빈도
- 섀도우 업데이트 작업
- Amazon S3 스토리지 기간

**비용 관리:**
- ✅ 정리 스크립트가 모든 리소스 제거
- ✅ 단기간 데모 리소스
- ✅ 구성 가능한 규모 (작게 시작)
- ⚠️ **완료 시 정리 스크립트 실행**

**📊 비용 모니터링:** [AWS Billing Dashboard](https://console.aws.amazon.com/billing/)

## 🚀 빠른 시작

```bash
# 1. 복제 및 설정
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # Windows에서: venv\Scripts\activate
pip install -r requirements.txt

# 2. AWS 구성
aws configure

# 3. 완전한 워크플로우 (권장 순서)
python scripts/provision_script.py        # 태그가 포함된 인프라 생성
python scripts/manage_dynamic_groups.py   # 디바이스 그룹 생성
python scripts/manage_packages.py         # 펌웨어 패키지 관리
python scripts/create_job.py              # 펌웨어 업데이트 배포
python scripts/simulate_job_execution.py  # 디바이스 업데이트 시뮬레이션
python scripts/explore_jobs.py            # 작업 진행 상황 모니터링
python scripts/manage_commands.py         # 디바이스에 실시간 명령 전송
python scripts/cleanup_script.py          # 리소스 식별을 통한 안전한 정리
```

## 📚 사용 가능한 스크립트

| 스크립트 | 목적 | 주요 기능 | 문서 |
|--------|---------|-------------|---------------|
| **provision_script.py** | 완전한 인프라 설정 | 디바이스, 그룹, 패키지, Amazon S3 스토리지 생성 | [📖 세부사항](docs/DETAILED_SCRIPTS.md#scriptsprovision_scriptpy) |
| **manage_dynamic_groups.py** | 동적 디바이스 그룹 관리 | Fleet Indexing 검증을 통한 생성, 목록, 삭제 | [📖 세부사항](docs/DETAILED_SCRIPTS.md#scriptsmanage_dynamic_groupspy) |
| **manage_packages.py** | 포괄적인 패키지 관리 | 패키지/버전 생성, Amazon S3 통합, 개별 되돌리기 상태를 통한 디바이스 추적 | [📖 세부사항](docs/DETAILED_SCRIPTS.md#scriptsmanage_packagespy) |
| **create_job.py** | OTA 업데이트 작업 생성 | 다중 그룹 타겟팅, 사전 서명된 URL | [📖 세부사항](docs/DETAILED_SCRIPTS.md#scriptscreate_jobpy) |
| **simulate_job_execution.py** | 디바이스 업데이트 시뮬레이션 | 실제 Amazon S3 다운로드, 가시적 계획 준비, 디바이스별 진행 상황 추적 | [📖 세부사항](docs/DETAILED_SCRIPTS.md#scriptssimulate_job_executionpy) |
| **explore_jobs.py** | 작업 모니터링 및 관리 | 대화형 작업 탐색, 취소, 삭제 및 분석 | [📖 세부사항](docs/DETAILED_SCRIPTS.md#scriptsexplore_jobspy) |
| **manage_commands.py** | 디바이스에 실시간 명령 전송 | 템플릿 관리, 명령 실행, 상태 모니터링, 기록 추적 | [📖 세부사항](docs/DETAILED_SCRIPTS.md#scriptsmanage_commandspy) |
| **cleanup_script.py** | AWS 리소스 제거 | 선택적 정리, 비용 관리 | [📖 세부사항](docs/DETAILED_SCRIPTS.md#scriptscleanup_scriptpy) |

> 📖 **상세 문서**: 포괄적인 스크립트 정보는 [docs/DETAILED_SCRIPTS.md](docs/DETAILED_SCRIPTS.md)를 참조하세요.

## ⚙️ 구성

**환경 변수** (선택사항):
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=ko                    # 기본 언어 설정 (en, es, fr 등)
```

**스크립트 기능**:
- **네이티브 AWS SDK**: 더 나은 성능과 안정성을 위해 boto3 사용
- **다국어 지원**: 영어로 폴백하는 대화형 언어 선택
- **디버그 모드**: 모든 AWS API 호출 및 응답 표시
- **병렬 처리**: 디버그 모드가 아닐 때 동시 작업
- **속도 제한**: 자동 AWS API 스로틀링 준수
- **진행 상황 추적**: 실시간 작업 상태
- **리소스 태깅**: 안전한 정리를 위한 자동 워크샵 태그
- **구성 가능한 명명**: 사용자 정의 가능한 디바이스 명명 패턴

### 리소스 태깅

모든 워크샵 스크립트는 정리 시 안전한 식별을 위해 생성된 리소스에 자동으로 `workshop=learning-aws-iot-dm-basics` 태그를 지정합니다. 이를 통해 워크샵에서 생성된 리소스만 삭제됩니다.

**태그가 지정된 리소스**:
- IoT Thing 유형
- IoT Thing 그룹 (정적 및 동적)
- IoT 소프트웨어 패키지
- IoT 작업
- Amazon S3 버킷
- AWS Identity and Access Management (IAM) 역할

**태그가 지정되지 않은 리소스** (명명 패턴으로 식별):
- IoT Thing (명명 규칙 사용)
- 인증서 (연결로 식별)
- Thing 섀도우 (연결로 식별)

### 디바이스 명명 구성

`--things-prefix` 매개변수로 디바이스 명명 패턴 사용자 정의:

```bash
# 기본 명명: Vehicle-VIN-001, Vehicle-VIN-002 등
python scripts/provision_script.py

# 사용자 정의 접두사: Fleet-Device-001, Fleet-Device-002 등
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# 정리용 사용자 정의 접두사 (프로비저닝 접두사와 일치해야 함)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```

**접두사 요구사항**:
- 영숫자, 하이픈, 밑줄, 콜론만 사용
- 최대 20자
- 순차 번호는 자동으로 0으로 채워짐 (001-999)

## 🌍 국제화 지원

모든 스크립트는 자동 언어 감지 및 대화형 선택을 통한 다국어를 지원합니다.

**언어 선택**:
- **대화형**: 스크립트가 첫 실행 시 언어 선택을 요청
- **환경 변수**: `AWS_IOT_LANG=ko` 설정으로 언어 선택 건너뛰기
- **폴백**: 누락된 번역에 대해 자동으로 영어로 폴백

**지원 언어**:
- **English (en)**: 완전한 번역 ✅
- **Spanish (es)**: 번역 준비 완료
- **Japanese (ja)**: 번역 준비 완료
- **Chinese (zh-CN)**: 번역 준비 완료
- **Portuguese (pt-BR)**: 번역 준비 완료
- **Korean (ko)**: 번역 준비 완료

**사용 예시**:
```bash
# 환경 변수를 통한 언어 설정 (자동화에 권장)
export AWS_IOT_LANG=ko
python scripts/provision_script.py

# 지원되는 대체 언어 코드
export AWS_IOT_LANG=spanish    # 또는 "es", "español"
export AWS_IOT_LANG=japanese   # 또는 "ja", "日本語", "jp"
export AWS_IOT_LANG=chinese    # 또는 "zh-cn", "中文", "zh"
export AWS_IOT_LANG=portuguese # 또는 "pt", "pt-br", "português"
export AWS_IOT_LANG=korean     # 또는 "ko", "한국어", "kr"

# 대화형 언어 선택 (기본 동작)
python scripts/manage_packages.py
# 출력: 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택
#         1. English
#         2. Español (Spanish)
#         3. 日本語 (Japanese)
#         4. 中文 (Chinese)
#         5. Português (Portuguese)
#         6. 한국어 (Korean)
#         Select language (1-6): 

# 모든 사용자 대면 텍스트가 선택된 언어로 표시됩니다
```

**메시지 카테고리**:
- **UI 요소**: 제목, 헤더, 구분자
- **사용자 프롬프트**: 입력 요청, 확인
- **상태 메시지**: 진행 상황 업데이트, 성공/실패 알림
- **오류 메시지**: 상세한 오류 설명 및 문제 해결
- **디버그 출력**: API 호출 정보 및 응답
- **학습 콘텐츠**: 교육적 순간 및 설명

## 📖 사용 예시

**완전한 워크플로우** (권장 순서):
```bash
python scripts/provision_script.py        # 1. 인프라 생성
python scripts/manage_dynamic_groups.py   # 2. 디바이스 그룹 생성
python scripts/manage_packages.py         # 3. 펌웨어 패키지 관리
python scripts/create_job.py              # 4. 펌웨어 업데이트 배포
python scripts/simulate_job_execution.py  # 5. 디바이스 업데이트 시뮬레이션
python scripts/explore_jobs.py            # 6. 작업 진행 상황 모니터링
python scripts/manage_commands.py         # 7. 디바이스에 실시간 명령 전송
python scripts/cleanup_script.py          # 8. 리소스 정리
```

**개별 작업**:
```bash
python scripts/manage_packages.py         # 패키지 및 버전 관리
python scripts/manage_dynamic_groups.py   # 동적 그룹 작업
```

> 📖 **더 많은 예시**: 상세한 사용 시나리오는 [docs/EXAMPLES.md](docs/EXAMPLES.md)를 참조하세요.

## 🛠️ 문제 해결

**일반적인 문제**:
- **자격 증명**: `aws configure`, 환경 변수 또는 AWS Identity and Access Management (IAM) 역할을 통해 AWS 자격 증명 구성
- **권한**: AWS Identity and Access Management (IAM) 사용자가 AWS IoT, Amazon S3, AWS Identity and Access Management (IAM) 권한을 가지고 있는지 확인
- **속도 제한**: 스크립트가 지능적 스로틀링으로 자동 처리
- **네트워크**: AWS API에 대한 연결 확인

**디버그 모드**: 상세한 문제 해결을 위해 모든 스크립트에서 활성화
```bash
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

> 📖 **상세 문제 해결**: 포괄적인 솔루션은 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)를 참조하세요.

## 🧹 중요: 리소스 정리

**지속적인 요금을 피하기 위해 완료 시 항상 정리를 실행하세요:**
```bash
python scripts/cleanup_script.py
# 옵션 1 선택: 모든 리소스
# 입력: DELETE
```

### 안전한 정리 기능

정리 스크립트는 워크샵 리소스만 삭제되도록 여러 식별 방법을 사용합니다:

1. **태그 기반 식별** (기본): `workshop=learning-aws-iot-dm-basics` 태그 확인
2. **명명 패턴 매칭** (보조): 알려진 워크샵 명명 규칙과 일치
3. **연결 기반** (3차): 워크샵 리소스에 연결된 리소스 식별

**정리 옵션**:
```bash
# 표준 정리 (대화형)
python scripts/cleanup_script.py

# 드라이런 모드 (삭제하지 않고 미리보기)
python scripts/cleanup_script.py --dry-run

# 사용자 정의 디바이스 접두사 (프로비저닝 접두사와 일치해야 함)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"

# 사용자 정의 접두사로 드라이런
python scripts/cleanup_script.py --dry-run --things-prefix "Fleet-Device-"
```

**정리가 제거하는 것:**
- 모든 AWS IoT 디바이스 및 그룹 (워크샵 태그 또는 일치하는 명명 패턴 포함)
- Amazon S3 버킷 및 펌웨어 파일 (태그 지정됨)
- AWS IoT 소프트웨어 패키지 (태그 지정됨)
- AWS IoT 명령 템플릿 (태그 지정됨)
- AWS Identity and Access Management (IAM) 역할 및 정책 (태그 지정됨)
- Fleet Indexing 구성
- 연결된 인증서 및 섀도우

**안전 기능**:
- 워크샵이 아닌 리소스는 자동으로 건너뜀
- 상세한 요약으로 삭제 및 건너뛴 리소스 표시
- 디버그 모드에서 각 리소스의 식별 방법 표시
- 드라이런 모드로 실제 삭제 전 미리보기 가능

## 🔧 개발자 가이드: 새 언어 추가

**메시지 파일 구조**:
```
i18n/
├── common.json                    # 모든 스크립트에서 공유되는 메시지
├── loader.py                      # 메시지 로딩 유틸리티
├── language_selector.py           # 언어 선택 인터페이스
└── {language_code}/               # 언어별 디렉토리
    ├── provision_script.json     # 스크립트별 메시지
    ├── manage_dynamic_groups.json
    ├── manage_packages.json
    ├── create_job.json
    ├── simulate_job_execution.json
    ├── explore_jobs.json
    └── cleanup_script.json
```

**새 언어 추가**:

1. **언어 디렉토리 생성**:
   ```bash
   mkdir i18n/{language_code}  # 예: 스페인어의 경우 i18n/es
   ```

2. **영어 템플릿 복사**:
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **메시지 파일 번역**:
   각 JSON 파일에는 분류된 메시지가 포함됩니다:
   ```json
   {
     "title": "📦 AWS IoT Software Package Manager (Boto3)",
     "separator": "============================================",
     "prompts": {
       "debug_mode": "🔧 Enable debug mode? [y/N]: ",
       "operation_choice": "Enter choice [1-11]: ",
       "continue_operation": "Continue? [Y/n]: "
     },
     "status": {
       "debug_enabled": "✅ Debug mode enabled",
       "package_created": "✅ Package created successfully",
       "clients_initialized": "🔍 DEBUG: Client configuration:"
     },
     "errors": {
       "invalid_choice": "❌ Invalid choice. Please enter 1-11",
       "package_not_found": "❌ Package '{}' not found",
       "api_error": "❌ Error in {} {}: {}"
     },
     "debug": {
       "api_call": "📤 API Call: {}",
       "api_response": "📤 API Response:",
       "debug_operation": "🔍 DEBUG: {}: {}"
     },
     "ui": {
       "operation_menu": "🎯 Select Operation:",
       "create_package": "1. Create Software Package",
       "goodbye": "👋 Thank you for using Package Manager!"
     },
     "learning": {
       "package_management_title": "Software Package Management",
       "package_management_description": "Educational content..."
     }
   }
   ```

4. **언어 선택기 업데이트** (새 언어 추가 시):
   `i18n/language_selector.py`에 언어 추가:
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Your Language Name",  # 새 옵션 추가
           # ... 기존 언어들
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "your_code",  # 새 언어 코드 추가
       # ... 기존 매핑들
   }
   ```

5. **번역 테스트**:
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**번역 가이드라인**:
- **형식 보존**: 이모지, 색상, 특수 문자 유지
- **플레이스홀더 유지**: 동적 콘텐츠를 위한 `{}` 플레이스홀더 유지
- **기술 용어**: AWS 서비스 이름은 영어로 유지
- **문화적 적응**: 예시와 참조를 적절히 적응
- **일관성**: 모든 파일에서 일관된 용어 사용

**메시지 키 패턴**:
- `title`: 스크립트 메인 제목
- `separator`: 시각적 구분자 및 분할선
- `prompts.*`: 사용자 입력 요청 및 확인
- `status.*`: 진행 상황 업데이트 및 작업 결과
- `errors.*`: 오류 메시지 및 경고
- `debug.*`: 디버그 출력 및 API 정보
- `ui.*`: 사용자 인터페이스 요소 (메뉴, 라벨, 버튼)
- `results.*`: 작업 결과 및 데이터 표시
- `learning.*`: 교육 콘텐츠 및 설명
- `warnings.*`: 경고 메시지 및 중요 알림
- `explanations.*`: 추가 컨텍스트 및 도움말 텍스트

**번역 테스트**:
```bash
# 특정 스크립트를 언어로 테스트
export AWS_IOT_LANG=your_language_code
python scripts/manage_packages.py

# 폴백 동작 테스트 (존재하지 않는 언어 사용)
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # 영어로 폴백되어야 함
```

## 📚 문서

- **[상세 스크립트](docs/DETAILED_SCRIPTS.md)** - 포괄적인 스크립트 문서
- **[사용 예시](docs/EXAMPLES.md)** - 실용적인 시나리오 및 워크플로우
- **[문제 해결](docs/TROUBLESHOOTING.md)** - 일반적인 문제 및 솔루션

## 📄 라이선스

MIT No Attribution License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🏷️ 태그

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot`