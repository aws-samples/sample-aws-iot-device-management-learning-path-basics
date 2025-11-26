# New Language Addition Template

This template provides a standardized process for adding new languages to the multilingual README system.

## 📋 Pre-Addition Checklist

Before starting the translation process, ensure:

- [ ] Language has native speaker available for translation
- [ ] Language has native speaker available for ongoing maintenance
- [ ] Language is supported in the project's i18n system
- [ ] Cultural context is understood for technical content
- [ ] Commitment exists for long-term maintenance

## 🌍 Language Information

**Complete this information before starting:**

| Field | Value |
|-------|-------|
| **Language Name (English)** | [e.g., French] |
| **Language Name (Native)** | [e.g., Français] |
| **ISO 639-1 Code** | [e.g., fr] |
| **Country Flag Emoji** | [e.g., 🇫🇷] |
| **Target File Name** | [e.g., README.fr.md] |
| **Primary Translator** | [Name and contact] |
| **Reviewer** | [Name and contact] |
| **Cultural Context Notes** | [Any special considerations] |

## 🔧 Implementation Steps

### Step 1: Create Base Translation File

```bash
# Copy main README as starting point
cp README.md README.[language_code].md
```

### Step 2: Update Language Navigation

Add your language to the navigation table in **ALL** existing README files:

**Current Navigation Table:**
```markdown
## 🌍 Available Languages | Idiomas Disponibles | 利用可能な言語 | 사용 가능한 언어 | Idiomas Disponíveis | 可用语言

| Language | README |
|----------|---------|
| 🇺🇸 English | [README.md](README.md) |
| 🇪🇸 Español | [README.es.md](README.es.md) |
| 🇯🇵 日本語 | [README.ja.md](README.ja.md) |
| 🇰🇷 한국어 | [README.ko.md](README.ko.md) |
| 🇧🇷 Português | [README.pt.md](README.pt.md) |
| 🇨🇳 中文 | [README.zh.md](README.zh.md) |
```

**Updated Navigation Table:**
```markdown
## 🌍 Available Languages | Idiomas Disponibles | 利用可能な言語 | 사용 가능한 언어 | Idiomas Disponíveis | 可用语言 | [Add your language]

| Language | README |
|----------|---------|
| 🇺🇸 English | [README.md](README.md) |
| 🇪🇸 Español | [README.es.md](README.es.md) |
| 🇯🇵 日本語 | [README.ja.md](README.ja.md) |
| 🇰🇷 한국어 | [README.ko.md](README.ko.md) |
| 🇧🇷 Português | [README.pt.md](README.pt.md) |
| 🇨🇳 中文 | [README.zh.md](README.zh.md) |
| [Flag] [Native Name] | [README.[code].md](README.[code].md) |
```

**Files to Update:**
- [ ] README.md
- [ ] README.es.md
- [ ] README.ja.md
- [ ] README.ko.md
- [ ] README.pt.md
- [ ] README.zh.md
- [ ] README.[your_language_code].md

### Step 3: Section-by-Section Translation

Use this checklist to ensure all sections are properly translated:

#### Header Section
- [ ] **Language Navigation**: Keep identical to other files
- [ ] **Project Title**: Translate main title
- [ ] **Project Description**: Translate description paragraph

#### Main Content Sections
- [ ] **Target Audience**: Translate and adapt culturally
- [ ] **Learning Objectives**: Translate all bullet points
- [ ] **Prerequisites**: Translate with cultural context
- [ ] **Cost Analysis**: Translate descriptions, adapt currency examples
- [ ] **Quick Start**: Translate instructions, preserve commands
- [ ] **Available Scripts**: Translate descriptions, preserve technical terms
- [ ] **Configuration**: Translate explanations, preserve code
- [ ] **Internationalization Support**: Translate and add language-specific examples
- [ ] **Usage Examples**: Translate comments, preserve commands
- [ ] **Troubleshooting**: Translate guidance, preserve technical terms
- [ ] **Resource Cleanup**: Translate instructions
- [ ] **Developer Guide**: Translate content, preserve code examples
- [ ] **Documentation**: Translate descriptions, preserve links
- [ ] **License**: Translate license text
- [ ] **Tags**: Keep in English

### Step 4: Content Preservation Rules

**MUST Keep in English:**
- [ ] AWS service names (AWS IoT Core, Amazon S3, etc.)
- [ ] Technical APIs and method names
- [ ] Code blocks and command examples
- [ ] File names and directory paths
- [ ] URLs and external links
- [ ] Environment variable names
- [ ] Script file names
- [ ] JSON keys and technical identifiers

**MUST Translate:**
- [ ] Section headings and descriptions
- [ ] User instructions and explanations
- [ ] Learning objectives and prerequisites
- [ ] Cost analysis descriptions
- [ ] Troubleshooting guidance
- [ ] User interface text and prompts

**MUST Keep Identical:**
- [ ] Language navigation table structure
- [ ] Markdown formatting and structure
- [ ] Table layouts and alignment
- [ ] Emoji usage and placement
- [ ] Link destinations and anchors

### Step 5: Cultural Adaptations

Consider these cultural adaptations while maintaining technical accuracy:

**Currency and Costs:**
- [ ] Include local currency context where appropriate
- [ ] Adapt cost examples to regional AWS pricing if significantly different
- [ ] Maintain USD as primary with local context as secondary

**Regional Considerations:**
- [ ] AWS service availability in target region
- [ ] Local compliance or regulatory considerations
- [ ] Time zone and date format preferences
- [ ] Cultural references in examples

**Technical Terminology:**
- [ ] Use established technical translations in target language
- [ ] Maintain consistency with existing AWS documentation in that language
- [ ] Create glossary of key terms for consistency

### Step 6: Quality Assurance

#### Self-Review Checklist
- [ ] All sections from main README present
- [ ] Navigation table identical across all files
- [ ] Technical terms preserved in English
- [ ] Code blocks unchanged from original
- [ ] All links functional and correct
- [ ] Grammar and spelling correct in target language
- [ ] Tone consistent with original professional style
- [ ] Cultural references appropriate for target audience
- [ ] Terminology consistent throughout document

#### Peer Review Process
- [ ] Native speaker review completed
- [ ] Technical accuracy verified
- [ ] Cultural appropriateness confirmed
- [ ] Consistency with existing translations checked
- [ ] Missing or incorrect content identified and fixed

#### Technical Validation
- [ ] File renders correctly in GitHub
- [ ] Navigation works between all language versions
- [ ] Mobile display acceptable
- [ ] Special characters display correctly
- [ ] Links work in various markdown environments

### Step 7: Integration and Testing

#### Automated Testing
Run validation scripts to check:
- [ ] Structure consistency across all README files
- [ ] Link functionality in new translation
- [ ] Navigation table consistency
- [ ] Technical content preservation

#### Manual Testing
- [ ] View file in GitHub web interface
- [ ] Test navigation between language versions
- [ ] Verify mobile responsiveness
- [ ] Check accessibility with screen readers
- [ ] Test in various markdown viewers

### Step 8: Documentation Updates

#### Update Project Documentation
- [ ] Add language to main project documentation
- [ ] Update any references to supported languages
- [ ] Include in automated validation scripts
- [ ] Update maintenance documentation

#### Create Language-Specific Notes
Document any special considerations for this language:
- [ ] Cultural adaptations made
- [ ] Technical terminology decisions
- [ ] Ongoing maintenance considerations
- [ ] Contact information for future updates

## 📝 Translation Guidelines Reference

### Tone and Style
- **Professional**: Maintain the educational and professional tone
- **Clear**: Use clear, concise language appropriate for technical documentation
- **Consistent**: Use consistent terminology throughout the document
- **Accessible**: Make content accessible to developers at associate level

### Technical Content Handling
- **Preserve Exactly**: Code blocks, commands, file paths, URLs
- **Translate Context**: Comments, explanations, user-facing text
- **Maintain Structure**: Keep all markdown formatting identical
- **Test Thoroughly**: Ensure all technical examples still work

### Cultural Sensitivity
- **Appropriate Examples**: Use culturally appropriate examples and references
- **Local Context**: Provide local context where helpful (currency, regulations)
- **Inclusive Language**: Use inclusive language appropriate for the culture
- **Professional Standards**: Maintain professional standards for the target culture

## 🔍 Validation Checklist

Before submitting the new language translation:

### Content Validation
- [ ] All sections translated and present
- [ ] Technical accuracy maintained
- [ ] Cultural adaptations appropriate
- [ ] Grammar and spelling correct
- [ ] Terminology consistent

### Technical Validation
- [ ] File structure identical to main README
- [ ] Navigation table works correctly
- [ ] All links functional
- [ ] Code blocks preserved exactly
- [ ] Markdown renders correctly

### Integration Validation
- [ ] Navigation updated in all existing README files
- [ ] New language accessible from all versions
- [ ] Automated tests pass
- [ ] Manual testing completed
- [ ] Documentation updated

## 📞 Support Resources

### Getting Help
- **Translation Questions**: Consult with native speakers and existing translations
- **Technical Issues**: Review main README.md and test thoroughly
- **Cultural Context**: Research target audience and cultural norms
- **Maintenance**: Review TRANSLATION_MAINTENANCE.md guide

### Useful Tools
- **Markdown Editors**: Use editors with live preview
- **Grammar Checkers**: Use language-specific grammar checking tools
- **Translation Memory**: Consider using translation memory tools for consistency
- **Validation Scripts**: Use provided scripts to check consistency

## 📋 Completion Checklist

Mark complete when finished:

- [ ] Language information form completed
- [ ] Base translation file created
- [ ] Navigation updated in all existing files
- [ ] All sections translated following guidelines
- [ ] Content preservation rules followed
- [ ] Cultural adaptations made appropriately
- [ ] Quality assurance completed (self and peer review)
- [ ] Technical validation passed
- [ ] Integration testing completed
- [ ] Documentation updated
- [ ] Maintenance contact established

**Final Review Date**: ___________
**Reviewer**: ___________
**Approved for Integration**: [ ] Yes [ ] No

---

**Notes and Special Considerations:**
[Add any language-specific notes, decisions made, or special considerations for future maintenance]