# Translation Templates and Tools

This directory contains templates and tools for maintaining the multilingual README system. Use these resources to ensure consistent, high-quality translations across all supported languages.

## 📁 Directory Structure

```
docs/templates/
├── README.md                           # This file
├── NEW_LANGUAGE_TEMPLATE.md            # Template for adding new languages
├── TRANSLATION_QA_CHECKLIST.md         # Quality assurance checklist
└── validation_scripts/                 # Automated validation tools
    ├── validate_readme_structure.py    # Structure consistency checker
    └── validate_readme_links.py        # Link validation tool
```

## 🚀 Quick Start

### For Translation Updates

1. **Review Changes**: Check what changed in the main README.md
2. **Use QA Checklist**: Copy `TRANSLATION_QA_CHECKLIST.md` and fill it out
3. **Update Translations**: Update each language file systematically
4. **Run Validation**: Use validation scripts to check consistency
5. **Complete QA**: Finish the checklist and get approval

### For Adding New Languages

1. **Use Template**: Copy and fill out `NEW_LANGUAGE_TEMPLATE.md`
2. **Follow Process**: Complete all steps in the template
3. **Run Validation**: Ensure new language integrates properly
4. **Update Documentation**: Add new language to all relevant docs

## 📋 Template Usage Guide

### NEW_LANGUAGE_TEMPLATE.md

**Purpose**: Standardized process for adding new languages to the README system.

**When to Use**:
- Adding support for a new language
- Onboarding new translators
- Ensuring consistent translation quality

**How to Use**:
1. Copy the template to a working document
2. Fill out the language information section
3. Follow each step systematically
4. Use the checklists to track progress
5. Complete quality assurance before integration

**Key Sections**:
- Pre-addition checklist and requirements
- Language information form
- Step-by-step implementation guide
- Content preservation rules
- Cultural adaptation guidelines
- Quality assurance procedures
- Integration and testing steps

### TRANSLATION_QA_CHECKLIST.md

**Purpose**: Comprehensive quality assurance for translation updates.

**When to Use**:
- After any changes to the main README.md
- Before committing translation updates
- For periodic quality reviews
- When onboarding new maintainers

**How to Use**:
1. Copy the checklist for each update session
2. Fill out the update information section
3. Work through each language systematically
4. Complete all validation steps
5. Get required approvals before committing

**Key Sections**:
- Update tracking and change documentation
- Per-language update status tracking
- Content preservation validation
- Link and rendering verification
- Cultural and language quality checks
- Automated validation integration
- Issue tracking and resolution
- Final approval process

## 🔧 Validation Scripts

### validate_readme_structure.py

**Purpose**: Automatically check structural consistency across all README files.

**Features**:
- Compares header count and hierarchy
- Validates navigation table presence
- Checks section order consistency
- Reports structural mismatches

**Usage**:
```bash
# Run from project root
python docs/templates/validation_scripts/validate_readme_structure.py

# Or run from templates directory (auto-detects project root)
cd docs/templates/validation_scripts
python validate_readme_structure.py
```

**Output Example**:
```
🔍 README Structure Validation
==================================================
📄 Main README (README.md):
   Headers: 24
   Navigation table: ✅ Found

📄 Checking README.es.md:
   ✅ Header count consistent (24)
   ✅ Header structure consistent
   ✅ Navigation table found
   ✅ Navigation table entries consistent (6)

✅ All README files have consistent structure!
```

### validate_readme_links.py

**Purpose**: Validate all links in README files are functional.

**Features**:
- Tests internal file links
- Validates external HTTP/HTTPS links
- Checks navigation consistency
- Caches external link results for efficiency
- Provides detailed error reporting

**Requirements**:
```bash
pip install requests
```

**Usage**:
```bash
# Run from project root
python docs/templates/validation_scripts/validate_readme_links.py

# Or run from templates directory
cd docs/templates/validation_scripts
python validate_readme_links.py
```

**Output Example**:
```
🔗 README Link Validation
==================================================
📄 Checking README.md:
   Found 15 links
   ✅ AWS IoT Core Learning Path: https://github.com/aws-samples/... (OK 200)
   ✅ Documentation: docs/DETAILED_SCRIPTS.md
   ❌ Broken Link: https://example.com/broken (HTTP 404)
   📊 Summary: 15 total, 8 internal, 7 external, 1 broken

🧭 Navigation Consistency Check
==================================================
✅ README.md: Navigation consistent
✅ README.es.md: Navigation consistent
```

## 🛠️ Customization and Extension

### Adding New Validation Scripts

To add new validation scripts:

1. **Create Script**: Add new Python script to `validation_scripts/`
2. **Follow Pattern**: Use existing scripts as templates
3. **Add Documentation**: Update this README with usage instructions
4. **Integrate**: Add to QA checklist if appropriate

**Script Template**:
```python
#!/usr/bin/env python3
"""
New Validation Script

Description of what this script validates.
"""

import os
import sys

def main():
    """Main validation function."""
    print("New Validation Tool")
    
    # Change to project root if needed
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..', '..')
    
    if os.path.exists(os.path.join(project_root, 'README.md')):
        os.chdir(project_root)
    
    # Perform validation
    success = validate_something()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

### Extending Templates

To modify or extend templates:

1. **Backup Original**: Keep a copy of the original template
2. **Document Changes**: Note what was modified and why
3. **Test Thoroughly**: Ensure changes work with existing process
4. **Update Documentation**: Reflect changes in this README

### Language-Specific Adaptations

For languages with special requirements:

1. **Document Requirements**: Add notes to templates
2. **Create Language Guide**: Consider separate guide for complex languages
3. **Update Scripts**: Modify validation scripts if needed
4. **Share Knowledge**: Document lessons learned

## 📚 Best Practices

### Template Usage

- **Always Use Templates**: Don't skip the systematic approach
- **Fill Out Completely**: Complete all sections and checklists
- **Keep Records**: Save completed templates for reference
- **Learn from Issues**: Update templates based on problems encountered

### Quality Assurance

- **Automate When Possible**: Use validation scripts consistently
- **Manual Review Critical**: Don't rely only on automation
- **Get Native Speaker Review**: Essential for quality translations
- **Test Thoroughly**: Check rendering and functionality

### Maintenance

- **Regular Updates**: Keep templates current with process changes
- **Script Maintenance**: Update validation scripts as needed
- **Documentation**: Keep this README updated
- **Training**: Use templates to train new contributors

## 🔍 Troubleshooting

### Common Issues

**Template Not Working**:
- Check if you're using the latest version
- Verify all prerequisites are met
- Review any error messages carefully
- Consult the main maintenance guide

**Validation Scripts Failing**:
- Ensure you're running from correct directory
- Check Python version and dependencies
- Verify file permissions
- Look for detailed error messages in output

**Quality Issues**:
- Review completed checklists for missed items
- Get additional native speaker review
- Check against existing high-quality translations
- Use validation scripts to catch technical issues

### Getting Help

1. **Check Documentation**: Review maintenance guide and templates
2. **Run Validation**: Use scripts to identify specific issues
3. **Review Examples**: Look at existing translations for patterns
4. **Ask for Review**: Get help from native speakers or maintainers

## 📞 Support

For questions about templates and tools:

- **Template Issues**: Review the template documentation and examples
- **Script Problems**: Check script comments and error messages
- **Process Questions**: Consult the main TRANSLATION_MAINTENANCE.md guide
- **Quality Concerns**: Get native speaker review and use QA checklist

## 🔄 Updates and Maintenance

This templates directory should be updated when:

- New languages are added to the system
- Translation process changes
- New validation requirements identified
- Issues found with existing templates
- Feedback received from users

**Update Process**:
1. Identify what needs to change
2. Update relevant templates and scripts
3. Test changes thoroughly
4. Update this README
5. Notify users of changes

---

**Last Updated**: [Date when templates were last modified]
**Version**: 1.0
**Maintainer**: [Contact information]