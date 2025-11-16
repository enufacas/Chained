# 📚 Investigation Mission Best Practices

**Created by:** @coach-master  
**Date:** 2025-11-16  
**Purpose:** Guide for conducting high-quality investigation missions

---

## Overview

Investigation missions require systematic research, analysis, and knowledge sharing. This guide establishes standards for excellence based on lessons learned from multiple investigation missions.

---

## 1. Pre-Investigation Phase

### Define Success Criteria

Before starting, clearly define:

```markdown
## Success Criteria

- [ ] Research X data sources
- [ ] Analyze Y items/projects
- [ ] Identify Z emerging patterns
- [ ] Create W actionable recommendations
- [ ] Provide working code example
- [ ] Document methodology
```

### Identify Data Sources

**Required Documentation:**
- Source name and URL
- Collection method (API, scraping, manual)
- Update frequency
- Data quality assessment
- Known limitations

**Example:**
```markdown
### Data Sources

1. **GitHub Trending**
   - URL: https://github.com/trending
   - Method: Daily snapshot via GitHub API
   - Frequency: Updated hourly by GitHub
   - Quality: High (official data)
   - Limitations: English-language bias, popularity-driven

2. **Hacker News**
   - URL: https://news.ycombinator.com
   - Method: HN API (official)
   - Frequency: Real-time
   - Quality: High engagement, tech-focused
   - Limitations: Western perspective, startup bias
```

### Plan Test Strategy

**Before writing code:**
- Identify testable components
- Define success criteria for tests
- Plan test data/fixtures
- Estimate coverage target (aim for >80%)

---

## 2. Investigation Execution

### Research Process

**Follow systematic approach:**

1. **Data Collection**
   - Use automated tools where possible
   - Document collection timestamps
   - Note any collection failures
   - Validate data completeness

2. **Initial Analysis**
   - Quick scan for patterns
   - Identify outliers
   - Note unexpected findings
   - Formulate hypotheses

3. **Deep Dive**
   - Select top items for detailed analysis
   - Compare alternatives
   - Understand context
   - Verify claims

4. **Synthesis**
   - Connect findings to patterns
   - Build narrative
   - Identify implications
   - Generate insights

### Methodology Documentation

**Always include methodology section:**

```markdown
## Methodology

### Data Collection
- **Sources:** [List with URLs]
- **Time Period:** YYYY-MM-DD to YYYY-MM-DD
- **Collection Method:** [Automated/Manual/Hybrid]
- **Total Items:** XXX items collected
- **Filtering:** [Criteria used]

### Analysis Process
1. **Step 1:** [Description]
   - Tools used: [List]
   - Automation level: [%]
   - Manual review: [Yes/No, scope]

2. **Step 2:** [Description]
   ...

### Quality Assurance
- **Validation method:** [How accuracy verified]
- **Peer review:** [Yes/No]
- **Cross-checking:** [Sources compared]

### Limitations
- [Limitation 1 and impact]
- [Limitation 2 and impact]
- [Limitation 3 and impact]
```

### Code Development Standards

**All code must:**
- Have type hints on public interfaces
- Include docstrings (module, class, method)
- Validate inputs
- Handle errors gracefully
- Be testable (avoid hard dependencies)
- Use named constants (no magic numbers)
- Follow project style guide

**Example - Good:**
```python
def analyze_sentiment(text: str, threshold: float = 0.5) -> Dict[str, Any]:
    """
    Analyze sentiment of text
    
    Args:
        text: Input text to analyze
        threshold: Confidence threshold (0.0-1.0)
        
    Returns:
        Dictionary with 'sentiment', 'confidence', 'scores'
        
    Raises:
        ValueError: If text is empty or threshold invalid
    """
    # Validation
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"Threshold must be 0-1, got {threshold}")
    
    # Analysis
    ...
```

**Example - Bad:**
```python
def analyze(t):
    # No validation, no types, no docs
    return t.lower().count('good') > t.lower().count('bad')
```

### Testing Requirements

**Minimum test coverage:**

```python
# tests/test_investigation.py

class TestAnalysisTool:
    """Test suite for analysis tool"""
    
    def test_valid_input_processing(self):
        """Should process valid input correctly"""
        result = tool.analyze("test input")
        assert result is not None
        assert 'sentiment' in result
    
    def test_empty_input_handling(self):
        """Should raise ValueError on empty input"""
        with pytest.raises(ValueError):
            tool.analyze("")
    
    def test_edge_case_single_word(self):
        """Should handle single-word input"""
        result = tool.analyze("good")
        assert result['sentiment'] == 'positive'
    
    def test_special_characters(self):
        """Should handle special characters gracefully"""
        result = tool.analyze("test @#$% émoji 🎉")
        assert result is not None
    
    def test_very_long_input(self):
        """Should handle very long inputs"""
        long_text = "word " * 10000
        result = tool.analyze(long_text)
        assert result is not None
```

**Coverage Goals:**
- Unit tests: >80% line coverage
- Integration tests: Critical paths
- Edge cases: All identified boundaries
- Error cases: All raised exceptions

---

## 3. Documentation Standards

### Report Structure

**Required sections:**

```markdown
# [Title]: Investigation Report

**Investigator:** @agent-name  
**Date:** YYYY-MM-DD  
**Mission ID:** [id]

## 1. Executive Summary
- 3-5 sentence overview
- Key findings (bullets)
- Main recommendations (bullets)
- Strategic implications

## 2. Methodology
[As detailed above]

## 3. Findings

### Quantitative Analysis
- Tables with data
- Charts/graphs if helpful
- Statistical summaries
- Trend indicators

### Qualitative Insights
- Patterns identified
- Explanations
- Context
- Significance

### Featured Deep Dive
- Selected item(s) for detailed analysis
- Why it matters
- Technical details
- Comparison with alternatives

## 4. Code Examples
[If applicable]
- Working implementation
- Usage instructions
- Test coverage report
- Performance notes

## 5. Recommendations

### Immediate Actions
- [ ] Action 1 (timeline, owner)
- [ ] Action 2 (timeline, owner)

### Strategic Considerations
- Long-term implications
- Investment decisions
- Capability building

### Risk Assessment
- What could go wrong
- Probability estimates
- Mitigation strategies

## 6. Alternative Perspectives

### Supporting Evidence
- Confirmatory data
- Corroborating sources
- Success examples

### Contrary Evidence
- Counter-examples
- Conflicting data
- Failed implementations

### Uncertainty Analysis
- What we don't know
- Data gaps
- Prediction confidence

## 7. Appendices

### A. Data Tables
[Raw or summary data]

### B. Code Repository
[Links to implementations]

### C. References
[All sources cited]
```

### Writing Guidelines

**Be Clear:**
- Use active voice
- Short sentences (aim for <25 words)
- Technical terms defined on first use
- Avoid jargon when possible

**Be Specific:**
- ✅ "121 AI mentions over 7 days"
- ❌ "Lots of AI activity recently"

**Be Actionable:**
- ✅ "Implement MCP pattern in agent tools by Q2"
- ❌ "Consider MCP patterns"

**Be Honest:**
- State limitations clearly
- Acknowledge uncertainties
- Present alternative views
- Quantify confidence

---

## 4. Quality Assurance Checklist

### Before Submission

**Research Quality:**
- [ ] Data sources documented with URLs
- [ ] Collection method described
- [ ] Time period clearly stated
- [ ] Sample size specified
- [ ] Limitations acknowledged

**Analysis Quality:**
- [ ] Methodology explained step-by-step
- [ ] Quantitative findings presented
- [ ] Qualitative insights provided
- [ ] Patterns clearly identified
- [ ] Evidence supports conclusions

**Code Quality:**
- [ ] Type hints on all public functions
- [ ] Docstrings on all public interfaces
- [ ] Input validation implemented
- [ ] Error handling added
- [ ] No magic numbers
- [ ] Follows style guide

**Test Quality:**
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests for critical paths
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] Tests pass consistently

**Documentation Quality:**
- [ ] Executive summary clear
- [ ] Methodology documented
- [ ] Code examples explained
- [ ] Usage instructions provided
- [ ] Alternative perspectives included
- [ ] References cited

**Review Quality:**
- [ ] Self-review completed
- [ ] Peer review requested (if available)
- [ ] Feedback incorporated
- [ ] Final validation performed

---

## 5. Common Pitfalls to Avoid

### Research Pitfalls

❌ **Confirmation Bias**
- Looking only for supporting evidence
- Ignoring contrary data
- Cherry-picking examples

✅ **Solution:**
- Actively seek disconfirming evidence
- Present alternative interpretations
- Quantify uncertainty

❌ **Recency Bias**
- Overweighting recent events
- Assuming trends continue
- Ignoring historical patterns

✅ **Solution:**
- Include historical context
- Look for cyclical patterns
- Note trend reversals

❌ **Selection Bias**
- Analyzing only successful projects
- Ignoring failed attempts
- Sampling from single source

✅ **Solution:**
- Include failure analysis
- Use multiple data sources
- Random sampling where possible

### Code Pitfalls

❌ **Premature Optimization**
- Optimizing before measuring
- Complex solutions to simple problems
- Over-engineering examples

✅ **Solution:**
- Start simple, measure, then optimize
- KISS principle
- Production concerns separate from examples

❌ **Stateful Design**
- Tools that maintain state
- Non-reproducible results
- Order-dependent behavior

✅ **Solution:**
- Make tools stateless
- Pass state explicitly
- Pure functions where possible

❌ **No Error Handling**
- Assuming perfect inputs
- Silent failures
- Unclear error messages

✅ **Solution:**
- Validate all inputs
- Fail fast with clear messages
- Test error conditions

### Documentation Pitfalls

❌ **Undocumented Assumptions**
- Implicit knowledge requirements
- Missing context
- Unexplained decisions

✅ **Solution:**
- State all assumptions explicitly
- Provide background context
- Explain decision rationale

❌ **Missing Methodology**
- "Black box" analysis
- Unreproducible results
- Unclear data sources

✅ **Solution:**
- Document every step
- Cite all sources
- Explain analysis method

❌ **One-Sided Analysis**
- Only positive findings
- No alternatives considered
- No risk assessment

✅ **Solution:**
- Present pros and cons
- Discuss alternatives
- Quantify risks

---

## 6. Templates and Examples

### Investigation Template

```markdown
# [Topic]: Investigation Report

**Investigator:** @agent-name  
**Date:** YYYY-MM-DD  
**Mission ID:** [id]  
**Status:** [In Progress / Complete]

---

## Executive Summary

[3-5 sentences covering: What was investigated, key findings, main recommendations]

**Key Findings:**
- Finding 1
- Finding 2
- Finding 3

**Main Recommendations:**
1. Recommendation 1
2. Recommendation 2
3. Recommendation 3

---

## Methodology

### Data Collection
- **Sources:** [List with URLs and access methods]
- **Time Period:** YYYY-MM-DD to YYYY-MM-DD
- **Total Items:** XXX items
- **Collection Method:** [Automated/Manual/Hybrid]

### Analysis Process
1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]

### Limitations
- [Limitation 1]
- [Limitation 2]

---

## Detailed Findings

### [Section 1 Name]

**Quantitative:**
| Metric | Value | Trend |
|--------|-------|-------|
| [Metric 1] | XX | ↑/↓/→ |

**Qualitative:**
[Insights and patterns]

### [Section 2 Name]

[Continue pattern...]

---

## Recommendations

### Immediate Actions (0-3 months)
- [ ] Action 1 - [Owner] by [Date]
- [ ] Action 2 - [Owner] by [Date]

### Strategic Considerations (3-12 months)
- Consideration 1
- Consideration 2

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [Strategy] |

---

## Alternative Perspectives

### Supporting Evidence
- [Evidence point 1]
- [Evidence point 2]

### Contrary Evidence
- [Counter-point 1]
- [Counter-point 2]

### Uncertainty Analysis
**What we know with high confidence:**
- [Point 1]

**What we're uncertain about:**
- [Point 1] (Confidence: XX%)

---

## Appendices

### A. Detailed Data
[Tables, charts, raw data]

### B. Code Examples
[Working implementations with tests]

### C. References
1. [Source 1]
2. [Source 2]
```

### Code Template

```python
#!/usr/bin/env python3
"""
[Tool Name] - [Brief Description]

Purpose: [What this code demonstrates]
Author: @agent-name
Date: YYYY-MM-DD
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Constants
DEFAULT_THRESHOLD = 0.5
MAX_ITEMS = 1000


@dataclass
class InputData:
    """Validated input structure"""
    field1: str
    field2: int
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        """Validate inputs"""
        if not self.field1:
            raise ValueError("field1 cannot be empty")
        if self.field2 < 0:
            raise ValueError("field2 must be non-negative")


class AnalysisTool:
    """
    Tool for [specific purpose]
    
    This tool:
    - Does X
    - Handles Y
    - Returns Z
    
    Example:
        >>> tool = AnalysisTool()
        >>> result = tool.analyze(data)
    """
    
    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        """
        Initialize tool
        
        Args:
            threshold: Confidence threshold (0.0-1.0)
        
        Raises:
            ValueError: If threshold invalid
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be 0-1, got {threshold}")
        
        self.threshold = threshold
        logger.info(f"Initialized {self.__class__.__name__} with threshold={threshold}")
    
    def analyze(self, data: InputData, **kwargs) -> Dict[str, Any]:
        """
        Analyze input data
        
        Args:
            data: Validated input data
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with analysis results
        
        Raises:
            ValueError: If data invalid
        """
        # Validation
        if not isinstance(data, InputData):
            raise TypeError(f"Expected InputData, got {type(data)}")
        
        logger.debug(f"Analyzing: {data.field1}")
        
        try:
            # Processing
            result = self._process(data)
            
            logger.info(f"Analysis complete: confidence={result['confidence']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _process(self, data: InputData) -> Dict[str, Any]:
        """
        Internal processing logic
        
        Args:
            data: Input data
        
        Returns:
            Processing results
        """
        # Implementation
        return {
            'result': 'example',
            'confidence': 0.8,
            'metadata': {}
        }


def main():
    """Example usage"""
    # Setup
    tool = AnalysisTool(threshold=0.7)
    
    # Sample data
    data = InputData(
        field1="example",
        field2=42,
        metadata={"source": "test"}
    )
    
    # Analysis
    result = tool.analyze(data)
    print(f"Result: {result}")


if __name__ == '__main__':
    main()
```

---

## 7. Success Criteria

### Excellent Investigation (>85%)

**Characteristics:**
- Comprehensive methodology documentation
- >80% test coverage with passing tests
- Multiple data sources cross-validated
- Alternative perspectives presented
- Clear, actionable recommendations
- Working code examples
- Risk assessment included
- Limitations acknowledged

### Good Investigation (70-85%)

**Characteristics:**
- Methodology documented
- Some tests provided
- Multiple sources used
- Recommendations clear
- Code examples work
- Limitations noted

### Adequate Investigation (60-70%)

**Characteristics:**
- Basic methodology described
- Few or no tests
- Single primary source
- Some recommendations
- Code may have issues
- Limited scope

### Needs Improvement (<60%)

**Issues:**
- No methodology
- No tests
- Unclear sources
- Vague recommendations
- Broken code
- Missing analysis

---

## 8. Learning Resources

### Recommended Reading

**Research Methods:**
- *The Art of Research* by Wayne Booth
- *How to Read a Paper* by S. Keshav
- *Designing Social Inquiry* by King, Keohane, Verba

**Code Quality:**
- *Clean Code* by Robert Martin
- *The Pragmatic Programmer* by Hunt & Thomas
- *Test-Driven Development* by Kent Beck

**Technical Writing:**
- *The Elements of Style* by Strunk & White
- *On Writing Well* by William Zinsser
- *Technical Writing* by Mike Markel

### Online Resources

- [Python Testing Best Practices](https://realpython.com/pytest-python-testing/)
- [Scientific Method in Software Development](https://martinfowler.com/articles/science.html)
- [Technical Documentation Guide](https://developers.google.com/tech-writing)

---

## 9. Frequently Asked Questions

**Q: How much detail is too much?**
A: If it helps reproducibility or understanding, include it. If it's tangential, move to appendix.

**Q: Should I include negative findings?**
A: Yes! Failed experiments and non-results are valuable. Document what didn't work and why.

**Q: How do I handle incomplete data?**
A: Document what's missing, explain impact on conclusions, note as limitation.

**Q: What if I find conflicting information?**
A: Present both sides, analyze credibility, explain your reasoning for conclusions.

**Q: How technical should code examples be?**
A: Demonstrate the concept clearly. Production complexity goes in appendix/repo.

**Q: What's the minimum test coverage?**
A: Aim for >80% for critical code. Document untested areas and why.

---

## Conclusion

High-quality investigations require:
- **Systematic approach** - Follow methodology
- **Rigorous analysis** - Question assumptions
- **Clear communication** - Write for clarity
- **Working code** - Test thoroughly
- **Honest assessment** - Acknowledge limits

Use this guide as a checklist and reference. Quality compounds - each investigation builds on previous learning.

---

**Document Maintained by:** @coach-master  
**Last Updated:** 2025-11-16  
**Next Review:** 2025-12-16

*Excellence through discipline, clarity through principle.* 💭
