# Translator Quick Start Guide

Welcome! This guide will help you get started with translating AWS IoT Device Management documentation.

## 📋 Before You Start

### Required Knowledge
- ✅ Native fluency in target language (es, ja, ko, pt, or zh)
- ✅ Technical writing experience
- ✅ Basic understanding of AWS IoT concepts
- ✅ Familiarity with Markdown formatting
- ✅ Experience with software documentation

### Required Tools
- Text editor with Markdown support (VS Code, Sublime, etc.)
- Git for version control
- Access to AWS IoT documentation in your language (for reference)

### Required Reading
1. **TRANSLATION_GLOSSARY.md** - Terminology reference (CRITICAL!)
2. **docs/TRANSLATION_MAINTENANCE.md** - Translation guidelines
4. **Existing README.{lang}.md** - Style reference for your language

---

## 🚀 Getting Started (5 Steps)

### Step 1: Choose Your Assignment
Check **TRANSLATION_PROGRESS_TRACKER.md** and select an available file:

**Priority Order**:
1. 🔴 TROUBLESHOOTING.{lang}.md (CRITICAL - Start here!)

### Step 2: Set Up Your Workspace
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd <repository-name>

# Create a new branch for your translation
git checkout -b translate-troubleshooting-es  # Example for Spanish

# Open the source file
# Source: docs/TROUBLESHOOTING.md
# Target: docs/TROUBLESHOOTING.es.md (create this file)
```

### Step 3: Review Reference Materials
Before translating, review:
- ✅ **TRANSLATION_GLOSSARY.md** - Your terminology bible
- ✅ **README.{lang}.md** - Style guide for your language
- ✅ **i18n/{lang}/*.json** - Existing translations for consistency

### Step 4: Translate the Document
Follow the **Translation Workflow** below

### Step 5: Submit for Review
```bash
# Save your work
git add docs/TROUBLESHOOTING.es.md  # Example

# Commit with clear message
git commit -m "feat(i18n): Add Spanish translation for TROUBLESHOOTING.md"

# Push to repository
git push origin translate-troubleshooting-es

# Create pull request for review
```

---

## 📝 Translation Workflow

### Phase 1: Preparation (15 minutes)
1. Read the entire English document
2. Note any unfamiliar technical terms
3. Check TRANSLATION_GLOSSARY.md for all technical terms
4. Review similar content in README.{lang}.md for style
5. Set up your translation file

### Phase 2: First Pass Translation (Main Work)
1. Translate section by section
2. **DO NOT TRANSLATE**:
   - AWS service names
   - File paths and script names
   - Code blocks and commands
   - Error codes
   - URLs
3. **DO TRANSLATE**:
   - Headings and titles
   - Explanatory text
   - Instructions
   - Comments in code examples
   - Error explanations

### Phase 3: Code Block Preservation
For each code block:
```markdown
# ✅ CORRECT - Translate comment, keep code
```bash
# Configurar credenciales de AWS
aws configure
```

# ❌ WRONG - Don't translate commands
```bash
# Configurar credenciales de AWS
aws configurar  # WRONG!
```
```

### Phase 4: Self-Review (30 minutes)
- [ ] All headings translated
- [ ] All paragraphs translated (except code)
- [ ] Code blocks preserved exactly
- [ ] Links functional
- [ ] Formatting intact (tables, lists, bullets)
- [ ] Technical terms match TRANSLATION_GLOSSARY.md
- [ ] No English text remaining (except code/commands)

### Phase 5: Quality Check (15 minutes)
Run through the **QA Checklist** below

---

## ✅ Quality Assurance Checklist

### Content Completeness
- [ ] All sections translated
- [ ] No missing paragraphs
- [ ] All headings present
- [ ] All lists complete

### Technical Accuracy
- [ ] AWS service names in English
- [ ] Technical terms from TRANSLATION_GLOSSARY.md
- [ ] Consistent with i18n JSON files
- [ ] Error messages explained correctly

### Code Preservation
- [ ] All code blocks unchanged
- [ ] Bash commands in English
- [ ] Python code in English
- [ ] JSON examples unchanged
- [ ] File paths unchanged

### Formatting
- [ ] Markdown syntax correct
- [ ] Tables formatted properly
- [ ] Lists indented correctly
- [ ] Code blocks have language tags
- [ ] Links work correctly

### Style Consistency
- [ ] Matches README.{lang}.md style
- [ ] Formal/polite tone maintained
- [ ] Consistent terminology throughout
- [ ] Natural flow in target language

---

## 🎯 Translation Examples

### Example 1: Heading Translation
```markdown
# English
## Common Issues

# Spanish
## Problemas Comunes

# Japanese
## よくある問題

# Korean
## 일반적인 문제

# Portuguese
## Problemas Comuns

# Chinese
## 常见问题
```

### Example 2: Mixed Content
```markdown
# English
To configure AWS credentials, run:
```bash
aws configure
```
Enter your Access Key ID and Secret Access Key.

# Spanish
Para configurar las credenciales de AWS, ejecute:
```bash
aws configure
```
Ingrese su Access Key ID y Secret Access Key.

# Note: "aws configure" stays in English!
# Note: "Access Key ID" and "Secret Access Key" stay in English (AWS terms)
```

### Example 3: Error Message Translation
```markdown
# English
**Problem**: "Unable to locate credentials"
**Solution**: Configure AWS credentials using `aws configure`

# Spanish
**Problema**: "Unable to locate credentials"
**Solución**: Configure las credenciales de AWS usando `aws configure`

# Note: Error message stays in English (matches AWS API)
# Note: Command stays in English
```

### Example 4: Technical Term Usage
```markdown
# English
The IoT Thing represents a physical device in AWS IoT Core.

# Spanish
La Cosa IoT representa un dispositivo físico en AWS IoT Core.

# Note: "Cosa" is from TRANSLATION_GLOSSARY.md
# Note: "AWS IoT Core" stays in English
```

---

## 🚫 Common Mistakes to Avoid

### ❌ Mistake 1: Translating AWS Service Names
```markdown
# WRONG
Amazon S3 → Amazon S3 (Spanish: Almacenamiento Simple)

# CORRECT
Amazon S3 → Amazon S3 (keep in English)
```

### ❌ Mistake 2: Translating Commands
```markdown
# WRONG
python scripts/provision_script.py
→ python scripts/script_de_aprovisionamiento.py

# CORRECT
python scripts/provision_script.py (keep unchanged)
```

### ❌ Mistake 3: Breaking Code Blocks
```markdown
# WRONG
```bash
# Configurar AWS
aws configurar  # Translated command!
```

# CORRECT
```bash
# Configurar AWS
aws configure  # Command stays in English
```
```

### ❌ Mistake 4: Inconsistent Terminology
```markdown
# WRONG - Using different terms for "Thing"
First paragraph: "dispositivo IoT"
Second paragraph: "cosa IoT"
Third paragraph: "objeto IoT"

# CORRECT - Use glossary term consistently
All paragraphs: "cosa IoT" (from TRANSLATION_GLOSSARY.md)
```

### ❌ Mistake 5: Translating File Paths
```markdown
# WRONG
docs/TROUBLESHOOTING.md → docs/SOLUCION_DE_PROBLEMAS.md

# CORRECT
docs/TROUBLESHOOTING.md (keep unchanged in text)
```

---

## 📚 Reference Quick Links

### Essential Documents
- **Glossary**: `TRANSLATION_GLOSSARY.md` - Check this FIRST for any technical term
- **Progress**: `TRANSLATION_PROGRESS_TRACKER.md` - Track your work
- **Guidelines**: `docs/TRANSLATION_MAINTENANCE.md` - Detailed guidelines

### Language-Specific References
- **Your README**: `README.{lang}.md` - Style guide for your language
- **Your i18n files**: `i18n/{lang}/*.json` - Existing translations
- **AWS Docs**: AWS documentation in your language (if available)

### Source Files to Translate
- `docs/TROUBLESHOOTING.md` - CRITICAL priority

---

## 💡 Pro Tips

### Tip 1: Use Find & Replace Wisely
When you encounter a repeated technical term:
1. Check TRANSLATION_GLOSSARY.md for the correct translation
2. Use Find & Replace to ensure consistency
3. But be careful with context-sensitive terms!

### Tip 2: Translate in Chunks
Don't try to translate the entire document in one sitting:
- Break it into sections (e.g., one major heading at a time)
- Take breaks to maintain quality
- Review each section before moving to the next

### Tip 3: Keep a Personal Glossary
As you translate, keep notes on:
- Terms you looked up
- Decisions you made about ambiguous phrases
- Questions for the reviewer

### Tip 4: Test Code Examples
If possible, test that code examples still work:
- Copy code blocks to a terminal
- Verify commands execute correctly
- Ensure no accidental modifications

### Tip 5: Read Aloud
After translating a section:
- Read it aloud in your language
- Does it sound natural?
- Would a native speaker understand it?

---

## 🆘 Getting Help

### Questions About...

**Technical Terms**
→ Check TRANSLATION_GLOSSARY.md first
→ Search i18n/{lang}/*.json files
→ Ask reviewer if still unclear

**AWS Concepts**
→ Check AWS documentation in your language
→ Review README.{lang}.md for context
→ Ask technical reviewer

**Style/Tone**
→ Review README.{lang}.md
→ Check similar sections in existing translations
→ Ask native speaker reviewer

**Markdown Formatting**
→ Check source file formatting
→ Use Markdown preview in your editor
→ Ask technical reviewer

---

## 📊 Time Estimates

Based on experience, expect these times per document:

| Document | Complexity | Estimated Time |
|----------|------------|----------------|
| TROUBLESHOOTING.md | MODERATE | 2-3 hours |

**Total per language**: 2-3 hours

**Note**: First document takes longer as you learn the process. Subsequent documents go faster.

---

## ✨ Success Criteria

Your translation is ready for review when:

- ✅ All content translated (except code/commands)
- ✅ All technical terms from TRANSLATION_GLOSSARY.md
- ✅ Code blocks preserved exactly
- ✅ Formatting intact
- ✅ Links functional
- ✅ Natural flow in target language
- ✅ QA checklist completed
- ✅ Self-review done

---

## 🎉 After Completion

1. Update TRANSLATION_PROGRESS_TRACKER.md
2. Submit pull request with clear description
3. Respond to reviewer feedback promptly
4. Celebrate your contribution! 🎊

---

## 📞 Contact

For questions or issues:
- Check existing documentation first
- Review TRANSLATION_GLOSSARY.md
- Ask your reviewer
- Update this guide if you find gaps!

---

**Good luck with your translation! Your work helps developers worldwide learn AWS IoT. 🌍**

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-26  
**For**: Translators working on documentation files
