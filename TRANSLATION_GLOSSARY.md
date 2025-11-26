# Translation Glossary

This glossary ensures consistent terminology across all documentation translations. Terms are extracted from existing i18n JSON files and AWS documentation.

## How to Use This Glossary

1. **Always check this glossary** before translating technical terms
2. **Use exact translations** provided for consistency
3. **Do NOT translate** terms marked as "Keep in English"
4. **Add new terms** if you encounter AWS-specific terminology not listed

---

## AWS Service Names (Keep in English)

These AWS service names should NEVER be translated:

| English | Translation Rule |
|---------|------------------|
| AWS IoT Core | Keep in English |
| AWS IoT Device Management | Keep in English |
| AWS IoT Jobs | Keep in English |
| AWS IoT Fleet Indexing | Keep in English |
| Amazon S3 | Keep in English |
| AWS IAM | Keep in English |
| AWS Lambda | Keep in English |
| Amazon CloudWatch | Keep in English |
| AWS SDK | Keep in English |
| boto3 | Keep in English |

---

## Technical Terms by Language

### Core IoT Concepts

| English | Spanish (es) | Japanese (ja) | Korean (ko) | Portuguese (pt) | Chinese (zh) |
|---------|-------------|---------------|-------------|-----------------|--------------|
| Thing | Cosa | モノ | 사물 | Coisa | 物品 |
| Thing Type | Tipo de Cosa | モノタイプ | 사물 유형 | Tipo de Coisa | 物品类型 |
| Thing Group | Grupo de Cosas | モノグループ | 사물 그룹 | Grupo de Coisas | 物品组 |
| Device | Dispositivo | デバイス | 디바이스 | Dispositivo | 设备 |
| Fleet | Flota | フリート | 플릿 | Frota | 车队 |
| Job | Trabajo | ジョブ | 작업 | Trabalho | 作业 |
| Job Execution | Ejecución de Trabajo | ジョブ実行 | 작업 실행 | Execução de Trabalho | 作业执行 |
| Shadow | Sombra | シャドウ | 섀도우 | Sombra | 影子 |
| Firmware | Firmware | ファームウェア | 펌웨어 | Firmware | 固件 |
| OTA Update | Actualización OTA | OTAアップデート | OTA 업데이트 | Atualização OTA | OTA更新 |
| Package | Paquete | パッケージ | 패키지 | Pacote | 软件包 |
| Version | Versión | バージョン | 버전 | Versão | 版本 |

### Job Status Terms

| English | Spanish (es) | Japanese (ja) | Korean (ko) | Portuguese (pt) | Chinese (zh) |
|---------|-------------|---------------|-------------|-----------------|--------------|
| IN_PROGRESS | EN_PROGRESO | 進行中 | 진행 중 | EM_PROGRESSO | 进行中 |
| COMPLETED | COMPLETADO | 完了 | 완료됨 | CONCLUÍDO | 已完成 |
| SUCCEEDED | EXITOSO | 成功 | 성공 | BEM-SUCEDIDO | 成功 |
| FAILED | FALLIDO | 失敗 | 실패 | FALHOU | 失败 |
| QUEUED | EN_COLA | キュー済み | 대기 중 | NA_FILA | 已排队 |
| CANCELED | CANCELADO | キャンセル済み | 취소됨 | CANCELADO | 已取消 |
| REJECTED | RECHAZADO | 拒否済み | 거부됨 | REJEITADO | 已拒绝 |
| TIMED_OUT | TIEMPO_AGOTADO | タイムアウト | 시간 초과 | TEMPO_ESGOTADO | 超时 |

### Configuration Terms

| English | Spanish (es) | Japanese (ja) | Korean (ko) | Portuguese (pt) | Chinese (zh) |
|---------|-------------|---------------|-------------|-----------------|--------------|
| Rollout | Despliegue | ロールアウト | 롤아웃 | Implantação | 推出 |
| Abort | Abortar | 中止 | 중단 | Abortar | 中止 |
| Timeout | Tiempo de espera | タイムアウト | 시간 초과 | Tempo limite | 超时 |
| Retry | Reintentar | 再試行 | 재시도 | Tentar novamente | 重试 |
| Rate Limit | Límite de velocidad | レート制限 | 속도 제한 | Limite de taxa | 速率限制 |
| Threshold | Umbral | しきい値 | 임계값 | Limite | 阈值 |
| Exponential | Exponencial | 指数関数的 | 지수 | Exponencial | 指数 |

### Script Operations

| English | Spanish (es) | Japanese (ja) | Korean (ko) | Portuguese (pt) | Chinese (zh) |
|---------|-------------|---------------|-------------|-----------------|--------------|
| Provision | Aprovisionar | プロビジョニング | 프로비저닝 | Provisionar | 配置 |
| Cleanup | Limpieza | クリーンアップ | 정리 | Limpeza | 清理 |
| Simulate | Simular | シミュレート | 시뮬레이션 | Simular | 模拟 |
| Explore | Explorar | 探索 | 탐색 | Explorar | 探索 |
| Manage | Gestionar | 管理 | 관리 | Gerenciar | 管理 |
| Create | Crear | 作成 | 생성 | Criar | 创建 |
| Delete | Eliminar | 削除 | 삭제 | Excluir | 删除 |
| Update | Actualizar | 更新 | 업데이트 | Atualizar | 更新 |

### User Interface Terms

| English | Spanish (es) | Japanese (ja) | Korean (ko) | Portuguese (pt) | Chinese (zh) |
|---------|-------------|---------------|-------------|-----------------|--------------|
| Debug Mode | Modo de depuración | デバッグモード | 디버그 모드 | Modo de depuração | 调试模式 |
| Verbose Mode | Modo detallado | 詳細モード | 상세 모드 | Modo detalhado | 详细模式 |
| Learning Goal | Objetivo de aprendizaje | 学習目標 | 학습 목표 | Objetivo de aprendizagem | 学习目标 |
| Press Enter | Presione Enter | Enterキーを押してください | Enter를 누르세요 | Pressione Enter | 按Enter键 |
| Enter choice | Ingrese opción | 選択を入力 | 선택 입력 | Digite a escolha | 输入选择 |
| Success | Éxito | 成功 | 성공 | Sucesso | 成功 |
| Failure | Fallo | 失敗 | 실패 | Falha | 失败 |
| Warning | Advertencia | 警告 | 경고 | Aviso | 警告 |
| Error | Error | エラー | 오류 | Erro | 错误 |

### Error Messages

| English | Spanish (es) | Japanese (ja) | Korean (ko) | Portuguese (pt) | Chinese (zh) |
|---------|-------------|---------------|-------------|-----------------|--------------|
| Invalid choice | Opción inválida | 無効な選択 | 잘못된 선택 | Escolha inválida | 无效选择 |
| Invalid number | Número inválido | 無効な数値 | 잘못된 숫자 | Número inválido | 无效数字 |
| Failed to | No se pudo | 失敗しました | 실패했습니다 | Falha ao | 失败 |
| Not found | No encontrado | 見つかりません | 찾을 수 없음 | Não encontrado | 未找到 |
| Access denied | Acceso denegado | アクセス拒否 | 액세스 거부됨 | Acesso negado | 访问被拒绝 |
| Connection error | Error de conexión | 接続エラー | 연결 오류 | Erro de conexão | 连接错误 |

---

## File and Path Terms (Keep in English)

These should remain in English as they are system paths:

- `scripts/provision_script.py`
- `scripts/cleanup_script.py`
- `scripts/create_job.py`
- `scripts/explore_jobs.py`
- `scripts/simulate_job_execution.py`
- `scripts/manage_dynamic_groups.py`
- `scripts/manage_packages.py`
- `i18n/`
- `docs/`
- `README.md`

---

## Command Terms (Keep in English)

All bash commands and Python code should remain in English:

```bash
python scripts/provision_script.py
aws configure
pip install -r requirements.txt
```

---

## Special Formatting Terms

### Emojis (Keep as-is)
Emojis are universal and should be kept:
- 🚀 (rocket)
- ✅ (checkmark)
- ❌ (cross)
- 🔍 (magnifying glass)
- 📚 (books)
- ⚠️ (warning)
- 🔧 (wrench)
- 📊 (chart)

### Status Indicators
- ✅ Complete
- ⬜ Not Started
- 🔄 In Progress
- ⚠️ Warning
- ❌ Error

---

## AWS-Specific Acronyms (Keep in English)

| Acronym | Full Name | Translation Rule |
|---------|-----------|------------------|
| IoT | Internet of Things | Keep "IoT" in English, optionally add translation in parentheses |
| OTA | Over-The-Air | Keep "OTA" in English |
| API | Application Programming Interface | Keep "API" in English |
| SDK | Software Development Kit | Keep "SDK" in English |
| IAM | Identity and Access Management | Keep "IAM" in English |
| S3 | Simple Storage Service | Keep "S3" in English |
| ARN | Amazon Resource Name | Keep "ARN" in English |
| VIN | Vehicle Identification Number | Keep "VIN" in English |
| JSON | JavaScript Object Notation | Keep "JSON" in English |
| CLI | Command Line Interface | Keep "CLI" in English |

---

## Context-Specific Translations

### "Thing" Translation Context

The word "Thing" in AWS IoT has specific meanings:

1. **As AWS IoT Thing**: Use the translations in the table above
2. **As general object**: Use standard translation for "thing/object" in your language
3. **In compound terms**: 
   - Thing Type → [Translation for Thing] + [Translation for Type]
   - Thing Group → [Translation for Thing] + [Translation for Group]

### "Job" Translation Context

1. **AWS IoT Job**: Use the translations in the table above
2. **General task/work**: Use standard translation for "job/task" in your language

---

## Translation Notes by Language

### Spanish (es)
- Use formal "usted" form for instructions
- Maintain gender agreement for technical terms
- Use Latin American Spanish conventions

### Japanese (ja)
- Use polite form (です/ます)
- Technical terms often use katakana
- Maintain consistent particle usage

### Korean (ko)
- Use formal polite form (합니다체)
- Technical terms often use English loanwords
- Maintain consistent honorific levels

### Portuguese (pt)
- Use Brazilian Portuguese conventions
- Maintain gender agreement
- Use formal "você" form for instructions

### Chinese (zh)
- Use Simplified Chinese characters
- Technical terms often use English directly
- Maintain consistent measure word usage

---

## Quality Assurance Checklist

When translating, verify:

- [ ] AWS service names kept in English
- [ ] Technical terms match this glossary
- [ ] File paths and commands in English
- [ ] Emojis preserved
- [ ] Status indicators consistent
- [ ] Code blocks unchanged
- [ ] Formatting preserved
- [ ] Links functional

---

## Adding New Terms

If you encounter a term not in this glossary:

1. Check existing i18n JSON files for the term
2. Check AWS documentation in the target language
3. Consult with native speaker reviewers
4. Add to this glossary with all language translations
5. Update TRANSLATION_MAINTENANCE.md

---

## References

- Existing i18n JSON files: `i18n/{lang}/*.json`
- AWS IoT Documentation: https://docs.aws.amazon.com/iot/
- Python boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

---

**Version**: 1.0  
**Last Updated**: 2025-11-26  
**Maintainer**: Translation Team
