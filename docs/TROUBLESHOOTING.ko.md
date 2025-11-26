# 문제 해결 가이드

이 문서는 AWS IoT Device Management 스크립트를 사용할 때 발생하는 일반적인 문제에 대한 해결책을 제공합니다.

## 일반적인 문제

### AWS 구성 문제

#### 문제: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**해결책**:
```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify configuration
aws sts get-caller-identity
```

#### 문제: "Access Denied" 오류
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**해결책**: AWS IAM 사용자/역할에 필요한 권한이 있는지 확인하세요:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:*",
                "iot-data:*",
                "iot-jobs-data:*",
                "s3:GetObject",
                "s3:PutObject",
                "s3:CreateBucket",
                "s3:DeleteBucket",
                "s3:ListBucket",
                "iam:GetRole",
                "iam:PassRole",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

#### 문제: "Region not configured"
```
You must specify a region
```

**해결책**:
```bash
# Set region in AWS CLI
aws configure set region us-east-1

# Or use environment variable
export AWS_DEFAULT_REGION=us-east-1
```

### 스크립트 실행 문제

#### 문제: "No module named 'colorama'"
```
ModuleNotFoundError: No module named 'colorama'
```

**해결책**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install colorama>=0.4.4 requests>=2.25.1
```

#### 문제: 스크립트가 멈추거나 시간 초과됨
**증상**: 스크립트가 실행 중에 멈춘 것처럼 보임

**해결책**:
1. 디버그 모드를 활성화하여 무슨 일이 일어나고 있는지 확인하세요:
   ```bash
   # When prompted, choose 'y' for debug mode
   🔧 Enable debug mode? [y/N]: y
   ```

2. AWS 서비스 제한 및 스로틀링을 확인하세요
3. 필요한 경우 병렬 워커를 줄이세요
4. 네트워크 연결을 확인하세요

#### 문제: "Thing type deletion requires 5-minute wait"
```
InvalidRequestException: Thing type cannot be deleted until 5 minutes after deprecation
```

**해결책**: 이것은 예상되는 동작입니다. 정리 스크립트는 다음과 같이 자동으로 처리합니다:
1. 먼저 사물 유형을 사용 중단합니다
2. 5분 동안 대기합니다
3. 그런 다음 삭제합니다

### 리소스 생성 문제

#### 문제: "Thing group already exists"
```
ResourceAlreadyExistsException: Thing group already exists
```

**해결책**: 이것은 일반적으로 무해합니다. 스크립트는 기존 리소스를 확인하고 이미 존재하는 경우 생성을 건너뜁니다.

#### 문제: "S3 bucket name already taken"
```
BucketAlreadyExists: The requested bucket name is not available
```

**해결책**: 스크립트는 타임스탬프를 사용하여 고유한 버킷 이름을 보장합니다. 이 문제가 발생하면:
1. 몇 초 기다렸다가 다시 시도하세요
2. 유사한 이름의 기존 버킷이 있는지 확인하세요

#### 문제: "Package version already exists"
```
ConflictException: Package version already exists
```

**해결책**: 스크립트는 먼저 기존 버전을 확인하여 이를 처리합니다. 업데이트가 필요한 경우:
1. 새 버전 번호를 사용하세요
2. 또는 먼저 기존 버전을 삭제하세요

### 작업 실행 문제

#### 문제: "No active jobs found"
```
❌ No active jobs found
```

**해결책**:
1. 먼저 `scripts/create_job.py`를 사용하여 작업을 생성하세요
2. 작업 상태를 확인하세요: `scripts/explore_jobs.py`
3. 작업이 취소되었거나 완료되었는지 확인하세요

#### 문제: "Failed to download artifact"
```
❌ Failed to download artifact: HTTP 403 Forbidden
```

**해결책**:
1. AWS IoT Jobs에 대한 AWS IAM 역할 권한을 확인하세요
2. 사전 서명된 URL 구성을 확인하세요
3. S3 버킷과 객체가 존재하는지 확인하세요
4. 사전 서명된 URL이 만료되지 않았는지 확인하세요(1시간 제한)

#### 문제: "Job execution not found"
```
ResourceNotFoundException: Job execution not found
```

**해결책**:
1. 작업 ID와 사물 이름이 올바른지 확인하세요
2. 디바이스가 대상 사물 그룹에 있는지 확인하세요
3. 작업이 여전히 활성 상태인지 확인하세요(완료/취소되지 않음)

### Fleet Indexing 문제

#### 문제: "Fleet Indexing queries return no results"
```
ℹ️ No devices currently match this query
```

**해결책**:
1. Fleet Indexing이 완료될 때까지 기다리세요(몇 분 걸릴 수 있음)
2. Fleet Indexing이 활성화되어 있는지 확인하세요
3. 쿼리 구문을 확인하세요
4. 디바이스에 예상되는 속성/섀도우가 있는지 확인하세요

#### 문제: "Invalid Fleet Indexing query"
```
InvalidRequestException: Invalid query string
```

**해결책**: 쿼리 구문을 확인하세요. 일반적인 문제:
- 디바이스 속성에는 `attributes.fieldName`을 사용하세요
- 클래식 섀도우에는 `shadow.reported.fieldName`을 사용하세요
- 명명된 섀도우에는 `shadow.name.\\$package.reported.fieldName`을 사용하세요
- 특수 문자를 올바르게 이스케이프하세요

### 성능 문제

#### 문제: "Rate limiting errors"
```
ThrottlingException: Rate exceeded
```

**해결책**: 스크립트에는 내장된 속도 제한이 있지만 이 문제가 발생하면:
1. 디버그 모드를 활성화하여 어떤 API가 제한되고 있는지 확인하세요
2. 스크립트의 병렬 워커를 줄이세요
3. 작업 간에 지연을 추가하세요
4. 계정의 AWS 서비스 제한을 확인하세요

#### 문제: "Scripts running slowly"
**증상**: 작업이 예상보다 훨씬 오래 걸림

**해결책**:
1. 네트워크 연결을 확인하세요
2. AWS 리전이 지리적으로 가까운지 확인하세요
3. 디버그 모드를 활성화하여 병목 현상을 식별하세요
4. 배치 크기를 줄이는 것을 고려하세요

### 데이터 일관성 문제

#### 문제: "Device shadows not updating"
```
❌ Failed to update device shadow
```

**해결책**:
1. IoT Data 엔드포인트 구성을 확인하세요
2. 디바이스/사물이 존재하는지 확인하세요
3. 섀도우 업데이트에서 올바른 JSON 형식을 보장하세요
4. 섀도우 작업에 대한 AWS IAM 권한을 확인하세요

#### 문제: "Package configuration not working"
```
❌ Failed to update global package configuration
```

**해결책**:
1. IoTPackageConfigRole이 존재하고 적절한 권한이 있는지 확인하세요
2. 역할 ARN이 올바르게 형식화되어 있는지 확인하세요
3. 리전에서 패키지 구성이 활성화되어 있는지 확인하세요

## 디버그 모드 사용

상세한 문제 해결을 위해 모든 스크립트에서 디버그 모드를 활성화하세요:

```bash
🔧 Enable debug mode (show all commands and outputs)? [y/N]: y
```

디버그 모드는 다음을 표시합니다:
- 실행 중인 모든 AWS CLI 명령
- API 요청 매개변수
- 전체 API 응답
- 오류 세부 정보 및 스택 추적

## 로그 분석

### 성공적인 작업
다음 지표를 찾으세요:
- ✅ 성공적인 작업에 대한 녹색 체크 마크
- 완료를 나타내는 진행률 카운터
- "completed successfully" 메시지

### 경고 신호
다음 패턴에 주의하세요:
- ⚠️ 노란색 경고(일반적으로 중요하지 않음)
- "already exists" 메시지(일반적으로 무해함)
- 시간 초과 경고

### 오류 패턴
일반적인 오류 지표:
- ❌ 실패에 대한 빨간색 X 표시
- "Failed to" 메시지
- 예외 스택 추적
- HTTP 오류 코드(403, 404, 500)

## 복구 절차

### 부분 프로비저닝 실패
프로비저닝이 중간에 실패한 경우:

1. **생성된 것을 확인하세요**:
   ```bash
   python scripts/explore_jobs.py
   # Option 1: List all jobs
   ```

2. **필요한 경우 정리하세요**:
   ```bash
   python scripts/cleanup_script.py
   # Option 1: ALL resources
   ```

3. **프로비저닝을 다시 시도하세요**:
   ```bash
   python scripts/provision_script.py
   # Scripts handle existing resources gracefully
   ```

### 실패한 작업 복구
실행 중에 작업이 실패한 경우:

1. **작업 상태를 확인하세요**:
   ```bash
   python scripts/explore_jobs.py
   # Option 2: Explore specific job
   ```

2. **개별 실패를 확인하세요**:
   ```bash
   python scripts/explore_jobs.py
   # Option 3: Explore job execution
   ```

3. **필요한 경우 롤백하세요**:
   ```bash
   python scripts/manage_packages.py
   # Select: 10. Revert Device Versions
   # Enter thing type and previous version
   ```

### 리소스 정리 문제
정리가 실패한 경우:

1. **선택적 정리를 시도하세요**:
   ```bash
   python scripts/cleanup_script.py
   # Option 2: Things only (then try groups)
   ```

2. **AWS 콘솔을 통한 수동 정리**:
   - AWS IoT Core → Manage → Things
   - AWS IoT Core → Manage → Thing groups
   - AWS IoT Core → Manage → Thing types
   - Amazon S3 → Buckets
   - AWS IAM → Roles

## 환경별 문제

### macOS 문제
- **SSL 경고**: 스크립트는 urllib3 SSL 경고를 자동으로 억제합니다
- **Python 버전**: Python 3.7+가 설치되어 있는지 확인하세요

### Windows 문제
- **경로 구분자**: 스크립트는 크로스 플랫폼 경로를 자동으로 처리합니다
- **PowerShell**: 적절한 실행 정책으로 명령 프롬프트 또는 PowerShell을 사용하세요

### Linux 문제
- **권한**: 스크립트에 실행 권한이 있는지 확인하세요
- **Python 경로**: `python` 대신 `python3`을 사용해야 할 수 있습니다

## AWS 서비스 제한

### 기본 제한(리전당)
- **Things**: 계정당 500,000개
- **Thing Types**: 계정당 100개
- **Thing Groups**: 계정당 500개
- **Jobs**: 100개의 동시 작업
- **API 속도 제한**: 
  - Thing 작업: 100 TPS(스크립트는 80 TPS 사용)
  - 동적 그룹: 5 TPS(스크립트는 4 TPS 사용)
  - 작업 실행: 200 TPS(스크립트는 150 TPS 사용)
  - 패키지 작업: 10 TPS(스크립트는 8 TPS 사용)

### 제한 증가 요청
더 높은 제한이 필요한 경우:
1. AWS 지원 센터로 이동하세요
2. "Service limit increase"에 대한 케이스를 생성하세요
3. 필요한 AWS IoT Core 제한을 지정하세요

## 도움 받기

### 상세 로깅 활성화
대부분의 스크립트는 상세 모드를 지원합니다:
```bash
🔧 Enable verbose mode? [y/N]: y
```

### AWS 서비스 상태 확인
- [AWS 서비스 상태 대시보드](https://status.aws.amazon.com/)
- AWS IoT Core 문제에 대한 특정 리전을 확인하세요

### 커뮤니티 리소스
- AWS IoT 개발자 포럼
- AWS 문서
- GitHub Issues(스크립트별 문제)

### 전문 지원
- AWS 지원(지원 플랜이 있는 경우)
- AWS 전문 서비스
- AWS 파트너 네트워크 컨설턴트

## 예방 팁

### 스크립트 실행 전
1. **AWS 구성 확인**: `aws sts get-caller-identity`
2. **권한 확인**: 먼저 작은 작업으로 테스트하세요
3. **리소스 제한 검토**: 계정 제한에 도달하지 않는지 확인하세요
4. **중요한 데이터 백업**: 기존 리소스를 수정하는 경우

### 실행 중
1. **진행 상황 모니터링**: 오류 패턴에 주의하세요
2. **중단하지 마세요**: 스크립트가 완료되도록 하거나 Ctrl+C를 신중하게 사용하세요
3. **AWS 콘솔 확인**: 리소스가 예상대로 생성되고 있는지 확인하세요

### 실행 후
1. **결과 확인**: 탐색 스크립트를 사용하여 결과를 확인하세요
2. **테스트 리소스 정리**: 임시 리소스에 대해 정리 스크립트를 사용하세요
3. **비용 모니터링**: 예상치 못한 요금에 대해 AWS 청구를 확인하세요

## 국제화 문제

### 문제: 스크립트가 번역된 텍스트 대신 원시 메시지 키를 표시함
**증상**: 스크립트가 실제 메시지 대신 `warnings.debug_warning` 및 `prompts.debug_mode`와 같은 텍스트를 표시함

**예시**:
```
🧹 AWS IoT Cleanup Script (Boto3)
===================================
📚 LEARNING GOAL:
This script demonstrates proper AWS IoT resource cleanup...
📍 Region: eu-west-1
🆔 Account ID: 278816698247
warnings.debug_warning
prompts.debug_mode
```

**근본 원인**: 이 문제는 다음과 같은 경우에 발생합니다:
1. 언어 선택기와 디렉토리 구조 간의 언어 코드 불일치
2. `get_message()` 함수에서 중첩된 키 처리 누락
3. 잘못된 메시지 파일 로딩

**해결책**:

1. **언어 코드 매핑 확인**: 언어 코드가 디렉토리 구조와 일치하는지 확인하세요:
   ```
   i18n/
   ├── en/     # English
   ├── es/     # Spanish  
   ├── ja/     # Japanese
   ├── ko/     # Korean
   ├── pt/     # Portuguese
   ├── zh/     # Chinese
   ```

2. **get_message() 구현 확인**: 스크립트는 점 표기법으로 중첩된 키를 처리해야 합니다:
   ```python
   def get_message(self, key, *args):
       """Get localized message with optional formatting"""
       # Handle nested keys like 'warnings.debug_warning'
       if '.' in key:
           keys = key.split('.')
           msg = messages
           for k in keys:
               if isinstance(msg, dict) and k in msg:
                   msg = msg[k]
               else:
                   msg = key  # Fallback to key if not found
                   break
       else:
           msg = messages.get(key, key)
       
       if args and isinstance(msg, str):
           return msg.format(*args)
       return msg
   ```

3. **언어 로딩 테스트**:
   ```bash
   # Test with environment variable
   export AWS_IOT_LANG=en
   python scripts/cleanup_script.py
   
   # Test different languages
   export AWS_IOT_LANG=es  # Spanish
   export AWS_IOT_LANG=ja  # Japanese
   export AWS_IOT_LANG=zh  # Chinese
   ```

4. **메시지 파일이 존재하는지 확인**:
   ```bash
   # Check if translation files exist
   ls i18n/en/cleanup_script.json
   ls i18n/es/cleanup_script.json
   # etc.
   ```

**예방**: 새 스크립트나 언어를 추가할 때:
- 작동하는 스크립트에서 올바른 `get_message()` 구현을 사용하세요
- 언어 코드가 디렉토리 이름과 정확히 일치하는지 확인하세요
- 배포 전에 여러 언어로 테스트하세요
- `docs/templates/validation_scripts/`의 검증 스크립트를 사용하세요

### 문제: 환경 변수로 언어 선택이 작동하지 않음
**증상**: `AWS_IOT_LANG`을 설정했음에도 불구하고 스크립트가 항상 언어 선택을 요청함

**해결책**:
1. **환경 변수 형식 확인**:
   ```bash
   # Supported formats
   export AWS_IOT_LANG=en        # English
   export AWS_IOT_LANG=english   # English
   export AWS_IOT_LANG=es        # Spanish
   export AWS_IOT_LANG=español   # Spanish
   export AWS_IOT_LANG=ja        # Japanese
   export AWS_IOT_LANG=japanese  # Japanese
   export AWS_IOT_LANG=zh        # Chinese
   export AWS_IOT_LANG=chinese   # Chinese
   export AWS_IOT_LANG=pt        # Portuguese
   export AWS_IOT_LANG=português # Portuguese
   export AWS_IOT_LANG=ko        # Korean
   export AWS_IOT_LANG=korean    # Korean
   ```

2. **환경 변수가 설정되어 있는지 확인**:
   ```bash
   echo $AWS_IOT_LANG
   ```

3. **언어 선택 테스트**:
   ```bash
   python3 -c "
   import sys, os
   sys.path.append('i18n')
   from language_selector import get_language
   print('Selected language:', get_language())
   "
   ```

### 문제: 새 언어에 대한 번역 누락
**증상**: 스크립트가 영어로 폴백하거나 지원되지 않는 언어에 대한 메시지 키를 표시함

**해결책**:
1. **언어 디렉토리 추가**: 새 언어에 대한 디렉토리 구조를 생성하세요
2. **번역 파일 복사**: 기존 번역을 템플릿으로 사용하세요
3. **언어 선택기 업데이트**: 지원되는 목록에 새 언어를 추가하세요
4. **철저히 테스트**: 모든 스크립트가 새 언어로 작동하는지 확인하세요

자세한 지침은 `docs/templates/NEW_LANGUAGE_TEMPLATE.md`를 참조하세요.

## AWS IoT Jobs API 제한 사항

### 문제: 완료된 작업에 대한 작업 실행 세부 정보에 액세스할 수 없음
**증상**: 완료, 실패 또는 취소된 작업에 대한 작업 실행 세부 정보를 탐색하려고 할 때 오류 발생

**오류 예시**:
```
❌ Error in Job Execution Detail upgradeSedanvehicle110_1761321268 on Vehicle-VIN-016: 
Job Execution has reached terminal state. It is neither IN_PROGRESS nor QUEUED
❌ Failed to get job execution details. Check job ID and thing name.
```

**근본 원인**: AWS는 작업 실행 세부 정보에 액세스하기 위한 두 가지 다른 API를 제공합니다:

1. **IoT Jobs Data API**(`iot-jobs-data` 서비스):
   - 엔드포인트: `describe_job_execution`
   - **제한 사항**: `IN_PROGRESS` 또는 `QUEUED` 상태의 작업에만 작동합니다
   - **오류**: 완료된 작업에 대해 "Job Execution has reached terminal state"를 반환합니다
   - **사용 사례**: 디바이스가 현재 작업 지침을 가져오도록 설계되었습니다

2. **IoT API**(`iot` 서비스):
   - 엔드포인트: `describe_job_execution`
   - **기능**: 모든 상태(COMPLETED, FAILED, CANCELED 등)의 작업에 대해 작동합니다
   - **제한 없음**: 과거 작업 실행 데이터에 액세스할 수 있습니다
   - **사용 사례**: 모든 작업 실행의 관리 및 모니터링을 위해 설계되었습니다

**해결책**: explore_jobs 스크립트가 IoT Jobs Data API 대신 IoT API를 사용하도록 업데이트되었습니다.

**코드 변경**:
```python
# Before (limited to active jobs only)
execution_response = self.iot_jobs_data_client.describe_job_execution(
    jobId=job_id,
    thingName=thing_name,
    includeJobDocument=True
)

# After (works for all job statuses)
execution_response = self.iot_client.describe_job_execution(
    jobId=job_id,
    thingName=thing_name
)
```

**검증**: 수정 후 이제 다음에 대한 작업 실행 세부 정보를 탐색할 수 있습니다:
- ✅ COMPLETED 작업
- ✅ FAILED 작업  
- ✅ CANCELED 작업
- ✅ IN_PROGRESS 작업
- ✅ QUEUED 작업
- ✅ 기타 작업 상태

**추가 이점**:
- 과거 작업 실행 데이터에 대한 액세스
- 실패한 배포에 대한 더 나은 문제 해결 기능
- 디바이스 업데이트 시도에 대한 완전한 감사 추적

### 문제: 실행 세부 정보에서 작업 문서를 사용할 수 없음
**증상**: 작업 실행 세부 정보는 표시되지만 작업 문서가 누락됨

**해결책**: 스크립트에 이제 폴백 메커니즘이 포함되어 있습니다:
1. 먼저 실행 세부 정보에서 작업 문서를 가져오려고 시도합니다
2. 사용할 수 없는 경우 기본 작업 세부 정보에서 검색합니다
3. 작업 문서를 사용할 수 없는 경우 적절한 메시지를 표시합니다

이를 통해 작업 상태나 API 제한 사항에 관계없이 디바이스로 전송된 작업 지침을 항상 볼 수 있습니다.
