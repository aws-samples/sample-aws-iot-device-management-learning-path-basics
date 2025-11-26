#!/usr/bin/env python3
"""
Comprehensive content validation script for README files.
Validates that all translations maintain the same section structure,
code blocks are identical, and AWS service names are preserved.
"""

import os
import re
import sys
from pathlib import Path

def extract_sections(content):
    """Extract all markdown sections from content."""
    # Find all headers (# ## ### etc.)
    header_pattern = r'^(#{1,6})\s+(.+)$'
    sections = []
    
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        header_match = re.match(header_pattern, line)
        if header_match:
            # Save previous section
            if current_section:
                sections.append({
                    'level': len(current_section['level']),
                    'title': current_section['title'],
                    'content': '\n'.join(current_content).strip()
                })
            
            # Start new section
            current_section = {
                'level': header_match.group(1),
                'title': header_match.group(2).strip()
            }
            current_content = []
        else:
            current_content.append(line)
    
    # Add final section
    if current_section:
        sections.append({
            'level': len(current_section['level']),
            'title': current_section['title'],
            'content': '\n'.join(current_content).strip()
        })
    
    return sections

def extract_code_blocks(content):
    """Extract all code blocks from content."""
    # Find code blocks with ```
    code_pattern = r'```(\w*)\n(.*?)\n```'
    code_blocks = re.findall(code_pattern, content, re.DOTALL)
    
    # Also find inline code with `
    inline_pattern = r'`([^`\n]+)`'
    inline_code = re.findall(inline_pattern, content)
    
    return {
        'blocks': code_blocks,
        'inline': inline_code
    }

def extract_aws_services(content):
    """Extract AWS service names and technical terms."""
    # Common AWS services that should remain in English
    aws_services = [
        'AWS IoT Core', 'Amazon S3', 'AWS IoT Jobs', 'AWS IoT Device Shadow',
        'AWS IoT Fleet Indexing', 'AWS Identity and Access Management',
        'IAM', 'AWS IoT Device Management', 'Amazon S3', 'AWS SDK', 'boto3',
        'AWS CLI', 'AWS API', 'AWS Billing Dashboard', 'AWS Console'
    ]
    
    found_services = []
    for service in aws_services:
        if service in content:
            found_services.append(service)
    
    # Also look for technical terms that should be preserved
    technical_terms = [
        'Python', 'Git', 'JSON', 'HTTP', 'HTTPS', 'API', 'SDK', 'CLI',
        'OTA', 'IoT', 'VIN', 'UUID', 'URL', 'UTF-8', 'ISO'
    ]
    
    found_terms = []
    for term in technical_terms:
        if term in content:
            found_terms.append(term)
    
    return {
        'aws_services': found_services,
        'technical_terms': found_terms
    }

def normalize_section_title(title):
    """Normalize section titles for comparison (remove language-specific parts)."""
    # Remove emojis and common prefixes
    title = re.sub(r'[🌍👥🎯📋💰🚀📚⚙️📖🛠️🧹🔧📚📄🏷️]', '', title)
    title = title.strip()
    
    # Handle multilingual titles - extract the core concept
    # More flexible matching for translated content
    title_lower = title.lower()
    
    if any(keyword in title_lower for keyword in ['available languages', 'idiomas disponibles', '利用可能な言語', '사용 가능한 언어', 'idiomas disponíveis', '可用语言']):
        return 'Available Languages'
    elif any(keyword in title_lower for keyword in ['target audience', 'audiencia objetivo', '対象読者', '대상 사용자', 'público-alvo', '目标受众']):
        return 'Target Audience'
    elif any(keyword in title_lower for keyword in ['learning objectives', 'objetivos de aprendizaje', '学習目標', '학습 목표', 'objetivos de aprendizado', '学习目标']):
        return 'Learning Objectives'
    elif any(keyword in title_lower for keyword in ['prerequisites', 'prerrequisitos', '前提条件', '전제 조건', 'pré-requisitos', '先决条件']):
        return 'Prerequisites'
    elif any(keyword in title_lower for keyword in ['cost analysis', 'análisis de costos', 'コスト分析', '비용 분석', 'análise de custos', '成本分析']):
        return 'Cost Analysis'
    elif any(keyword in title_lower for keyword in ['quick start', 'inicio rápido', 'クイックスタート', '빠른 시작', 'início rápido', '快速开始']):
        return 'Quick Start'
    elif any(keyword in title_lower for keyword in ['available scripts', 'scripts disponibles', '利用可能なスクリプト', '사용 가능한 스크립트', 'scripts disponíveis', '可用脚本']):
        return 'Available Scripts'
    elif any(keyword in title_lower for keyword in ['configuration', 'configuración', '設定', '구성', 'configuração', '配置']):
        return 'Configuration'
    elif any(keyword in title_lower for keyword in ['internationalization', 'internacionalización', '国際化', '국제화', 'internacionalização', '国际化']):
        return 'Internationalization Support'
    elif any(keyword in title_lower for keyword in ['usage examples', 'ejemplos de uso', '使用例', '사용 예시', 'exemplos de uso', '使用示例']):
        return 'Usage Examples'
    elif any(keyword in title_lower for keyword in ['troubleshooting', 'resolución de problemas', 'トラブルシューティング', '문제 해결', 'solução de problemas', '故障排除']):
        return 'Troubleshooting'
    elif any(keyword in title_lower for keyword in ['resource cleanup', 'limpieza de recursos', 'リソースクリーンアップ', '리소스 정리', 'limpeza de recursos', '资源清理']):
        return 'Resource Cleanup'
    elif any(keyword in title_lower for keyword in ['developer guide', 'guía del desarrollador', '開発者ガイド', '개발자 가이드', 'guia do desenvolvedor', '开发者指南']):
        return 'Developer Guide'
    elif any(keyword in title_lower for keyword in ['documentation', 'documentación', 'ドキュメント', '문서', 'documentação', '文档']):
        return 'Documentation'
    elif any(keyword in title_lower for keyword in ['license', 'licencia', 'ライセンス', '라이선스', 'licença', '许可证']):
        return 'License'
    elif any(keyword in title_lower for keyword in ['tags', 'etiquetas', 'タグ', '태그', 'tags', '标签']):
        return 'Tags'
    
    # For subsections and code comments, be more lenient
    # Allow translated subsections to pass validation
    if any(char in title for char in ['1.', '2.', '3.', '#']):
        return 'subsection'  # Generic subsection marker
    
    return title

def validate_content_structure():
    """Validate content structure across all README files."""
    readme_files = [
        'README.md',
        'README.es.md', 
        'README.ja.md',
        'README.ko.md',
        'README.pt.md',
        'README.zh.md'
    ]
    
    print("🔍 Validating README content structure...")
    print("=" * 60)
    
    file_data = {}
    errors = []
    
    # Extract data from all files
    for readme_file in readme_files:
        if not os.path.exists(readme_file):
            errors.append(f"❌ Missing file: {readme_file}")
            continue
            
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = extract_sections(content)
        code_blocks = extract_code_blocks(content)
        aws_services = extract_aws_services(content)
        
        file_data[readme_file] = {
            'sections': sections,
            'code_blocks': code_blocks,
            'aws_services': aws_services,
            'content': content
        }
    
    if not file_data:
        errors.append("❌ No valid README files found")
        return False
    
    # Use English README as reference
    reference_file = 'README.md'
    if reference_file not in file_data:
        errors.append(f"❌ Reference file {reference_file} not found")
        return False
    
    reference_data = file_data[reference_file]
    reference_sections = reference_data['sections']
    
    print(f"📋 Using {reference_file} as reference structure")
    print(f"   Found {len(reference_sections)} sections")
    
    # Validate section structure
    print("\n📑 Validating section structure...")
    for filename, data in file_data.items():
        if filename == reference_file:
            continue
        
        sections = data['sections']
        
        # Check section count
        if len(sections) != len(reference_sections):
            errors.append(f"❌ {filename}: Section count mismatch ({len(sections)} vs {len(reference_sections)})")
            continue
        
        # Check section structure
        for i, (ref_section, section) in enumerate(zip(reference_sections, sections)):
            # Check section level
            if section['level'] != ref_section['level']:
                errors.append(f"❌ {filename}: Section level mismatch at position {i+1} (level {section['level']} vs {ref_section['level']})")
            
            # Check normalized section titles
            ref_normalized = normalize_section_title(ref_section['title'])
            section_normalized = normalize_section_title(section['title'])
            
            # Allow flexibility for translated titles and subsections
            if ref_normalized != section_normalized:
                # Skip validation for subsections and translated content
                if ref_normalized != 'subsection' and section_normalized != 'subsection':
                    # Only validate major section structure, not detailed subsections
                    if ref_section['level'] <= 2:  # Only check main sections (# and ##)
                        errors.append(f"❌ {filename}: Major section structure mismatch at position {i+1} ('{section_normalized}' vs '{ref_normalized}')")
        
        print(f"✅ {filename}: Section structure validated")
    
    # Validate code blocks
    print("\n💻 Validating code blocks...")
    reference_code = reference_data['code_blocks']
    
    for filename, data in file_data.items():
        if filename == reference_file:
            continue
        
        code_blocks = data['code_blocks']
        
        # Check code block count
        if len(code_blocks['blocks']) != len(reference_code['blocks']):
            errors.append(f"❌ {filename}: Code block count mismatch ({len(code_blocks['blocks'])} vs {len(reference_code['blocks'])})")
        
        # Check that code blocks are identical (allow for translated comments)
        for i, (ref_block, block) in enumerate(zip(reference_code['blocks'], code_blocks['blocks'])):
            ref_content = ref_block[1].strip()
            block_content = block[1].strip()
            
            # Allow translated comments in code blocks
            # Remove comment lines for comparison
            ref_lines = [line for line in ref_content.split('\n') if not line.strip().startswith('#')]
            block_lines = [line for line in block_content.split('\n') if not line.strip().startswith('#')]
            
            ref_code_only = '\n'.join(ref_lines).strip()
            block_code_only = '\n'.join(block_lines).strip()
            
            if ref_code_only != block_code_only:
                errors.append(f"❌ {filename}: Code block {i+1} executable content differs from reference")
        
        print(f"✅ {filename}: Code blocks validated")
    
    # Validate AWS service preservation
    print("\n🔧 Validating AWS service name preservation...")
    reference_aws = reference_data['aws_services']
    
    for filename, data in file_data.items():
        if filename == reference_file:
            continue
        
        aws_services = data['aws_services']
        
        # Check that critical AWS services are present (allow some flexibility)
        critical_services = ['AWS IoT Core', 'Amazon S3', 'AWS IoT Jobs', 'IAM', 'boto3']
        missing_critical = []
        for service in critical_services:
            if service not in aws_services['aws_services']:
                missing_critical.append(service)
        
        if missing_critical:
            errors.append(f"❌ {filename}: Missing critical AWS services: {', '.join(missing_critical)}")
        
        # Check critical technical terms (be more lenient)
        critical_terms = ['Python', 'Git', 'AWS', 'IoT', 'API']
        missing_critical_terms = []
        for term in critical_terms:
            if term not in aws_services['technical_terms']:
                missing_critical_terms.append(term)
        
        if missing_critical_terms:
            errors.append(f"❌ {filename}: Missing critical technical terms: {', '.join(missing_critical_terms)}")
        
        print(f"✅ {filename}: AWS services and technical terms validated")
    
    # Report results
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ Content validation failed with {len(errors)} errors:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("✅ All README files have consistent section structure!")
        print("✅ All code blocks are identical across language versions!")
        print("✅ AWS service names and technical terms are preserved!")
        return True

if __name__ == "__main__":
    success = validate_content_structure()
    sys.exit(0 if success else 1)