# 문제 해결 가이드

이 가이드는 환경 설정 문제를 다룹니다. 스크립트별 문제의 경우 스크립트 실행 시 디버그 모드를 활성화하세요 - 상황에 맞는 오류 메시지와 안내를 제공합니다.

## 환경 설정

### AWS 자격 증명 구성

#### 문제: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**해결책**:
```bash
# AWS 자격 증명 구성
aws configure
# 입력: Access Key ID, Secret Access Key, 리전, 출력 형식

# 구성 확인
aws sts get-caller-identity
```

**대체 방법**:
- 환경 변수: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- AWS 자격 증명 파일: `~/.aws/credentials`
- IAM 역할 (EC2/Lambda 실행용)

---

### 리전 구성

#### 문제: "Region not configured" 또는 "You must specify a region"

**해결책**:
```bash
# AWS CLI에서 리전 설정
aws configure set region us-east-1

# 또는 환경 변수 사용
export AWS_DEFAULT_REGION=us-east-1

# 리전 확인
aws configure get region
```

**지원되는 리전**: IoT Core 서비스를 사용할 수 있는 모든 AWS 리전

---

### Python 종속성

#### 문제: "No module named 'colorama'" 또는 유사한 가져오기 오류
```
ModuleNotFoundError: No module named 'colorama'
```

**해결책**:
```bash
# 모든 종속성 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**설치 확인**:
```bash
python -c "import boto3, colorama, requests; print('모든 종속성이 설치되었습니다')"
```

---

### IAM 권한

#### 문제: "Access Denied" 또는 "User is not authorized" 오류
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**해결책**: AWS IAM 사용자/역할에 필요한 권한이 있는지 확인하세요:

**필수 IAM 작업**:
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
                "s3:PutBucketTagging",
                "iam:GetRole",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "iam:TagRole",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

**참고**: 프로덕션 환경의 경우 최소 권한 원칙을 따르고 리소스를 적절히 제한하세요.

---

## 도움 받기

### 스크립트별 문제

스크립트 실행 중 문제가 발생하면:

1. **디버그 모드 활성화** - 자세한 API 호출 및 응답 표시
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **오류 메시지 읽기** - 스크립트는 상황에 맞는 안내를 제공합니다

3. **교육적 일시 정지 확인** - 개념과 요구 사항을 설명합니다

4. **전제 조건 확인** - 대부분의 스크립트는 먼저 `provision_script.py`를 실행해야 합니다

### 일반적인 워크플로

```bash
# 1. 환경 설정 (한 번만)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. 인프라 생성 (먼저 실행)
python scripts/provision_script.py

# 3. 필요에 따라 다른 스크립트 실행
python scripts/manage_packages.py
python scripts/create_job.py
# 등

# 4. 완료 후 정리
python scripts/cleanup_script.py
```

### 추가 리소스

- **README.md** - 프로젝트 개요 및 빠른 시작
- **스크립트 i18n 메시지** - 귀하의 언어로 현지화된 안내
- **교육적 일시 정지** - 스크립트 실행 중 상황별 학습
- **AWS IoT 문서** - https://docs.aws.amazon.com/ko_kr/iot/
