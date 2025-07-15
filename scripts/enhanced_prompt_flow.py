"""
Enhanced Multi-Stage Prompt Flow for CloudFormation MCP
"""

class ConversationalPromptFlow:
    def __init__(self):
        self.stages = {
            "DISCOVERY": self._create_discovery_prompt,
            "REFINEMENT": self._create_refinement_prompt,
            "VALIDATION": self._create_validation_prompt,
            "GENERATION": self._create_generation_prompt
        }
    
    def get_next_prompt(self, stage: str, context: dict, llm_response: str = None):
        """Generate the next prompt in the conversation flow"""
        
        if stage == "DISCOVERY":
            return self._create_discovery_prompt(context)
        elif stage == "REFINEMENT" and llm_response:
            return self._create_refinement_prompt(context, llm_response)
        elif stage == "VALIDATION" and llm_response:
            return self._create_validation_prompt(context, llm_response)
        elif stage == "GENERATION":
            return self._create_generation_prompt(context)
    
    def _create_discovery_prompt(self, context):
        """First stage: Intelligent discovery of requirements"""
        user_request = context.get("description", "")
        detected_patterns = context.get("patterns", {})
        
        return f"""
You are an expert AWS Solutions Architect conducting a requirements discovery session.

USER REQUEST: "{user_request}"

INITIAL ANALYSIS:
- Detected Architecture: {detected_patterns.get('architecture', 'Unknown')}
- Confidence: {detected_patterns.get('confidence', 0)}%
- Potential Compliance: {detected_patterns.get('compliance', [])}

YOUR TASK: Ask 3-5 intelligent clarifying questions to understand:

1. **Architecture Clarity**: If confidence < 80%, ask specific questions to disambiguate
   - "When you say 'web application', do you mean a static site, API backend, or full-stack app?"
   - "Are you processing data in real-time streams or batch jobs?"

2. **Scale & Performance**: Always ask about scale
   - "What's your expected traffic volume? (requests/second, concurrent users, data volume)"
   - "Do you need multi-region deployment for disaster recovery?"

3. **Integration Points**: Understand the ecosystem
   - "What existing systems does this need to integrate with?"
   - "Are you using any specific CI/CD tools or deployment pipelines?"

4. **Constraints & Requirements**: Uncover hidden requirements
   - "Do you have budget constraints or preferred instance types?"
   - "Any compliance requirements (HIPAA, PCI-DSS, SOX)?"
   - "What's your RTO/RPO for disaster recovery?"

5. **Context-Specific Questions**: Based on detected patterns, ask targeted questions

RESPONSE FORMAT:
```
CLARIFYING QUESTIONS:
1. [Specific question based on ambiguity]
2. [Scale/performance question]
3. [Integration question]
4. [Constraints question]
5. [Pattern-specific question]

ASSUMPTIONS I'M MAKING:
- [List key assumptions you're making about their requirements]

NEXT STEPS:
- Once you answer these questions, I'll create a comprehensive architecture plan
```

Be conversational but professional. Focus on the most important unknowns first.
"""

    def _create_refinement_prompt(self, context, discovery_response):
        """Second stage: Refine requirements based on discovery"""
        
        return f"""
You are an expert AWS Solutions Architect refining the architecture requirements.

ORIGINAL REQUEST: "{context.get('description')}"

USER'S CLARIFICATIONS: 
{discovery_response}

YOUR TASK: Create a comprehensive requirements specification that will guide template generation.

ANALYZE THE RESPONSES:
1. **Extract Key Requirements**: Pull out specific technical requirements
2. **Identify Gaps**: What's still unclear or missing?
3. **Suggest Improvements**: Based on AWS best practices, what should they consider?

CREATE A REFINED SPECIFICATION:

```
ARCHITECTURE SPECIFICATION:

Core Requirements:
- [Specific technical requirements from their responses]
- [Performance/scale requirements with numbers]
- [Integration requirements]

Recommended Enhancements:
- [Security improvements they should consider]
- [Performance optimizations]
- [Cost optimization opportunities]
- [Operational excellence additions]

Architecture Decisions:
- [Key architectural choices and rationale]
- [Service selections with justification]
- [Trade-offs being made]

Still Need Clarification:
- [Any remaining ambiguities]
- [Decisions they need to make]
```

If there are still significant gaps, ask 1-2 follow-up questions. Otherwise, confirm you're ready to generate the CloudFormation template.
"""

    def _create_validation_prompt(self, context, refined_spec):
        """Third stage: Validate the architecture before generation"""
        
        return f"""
You are an expert AWS Solutions Architect performing final validation.

REFINED SPECIFICATION:
{refined_spec}

YOUR TASK: Perform a final architecture review and validation.

VALIDATION CHECKLIST:

1. **Architecture Soundness**:
   - Are all components properly integrated?
   - Are there any single points of failure?
   - Is the data flow logical and efficient?

2. **Security Review**:
   - Is data encrypted at rest and in transit?
   - Are IAM permissions following least privilege?
   - Are network security groups properly configured?

3. **Operational Excellence**:
   - Is monitoring and alerting comprehensive?
   - Are backup and recovery procedures defined?
   - Is the solution maintainable and scalable?

4. **Cost Optimization**:
   - Are resources right-sized?
   - Are there opportunities for reserved instances or savings plans?
   - Is auto-scaling configured appropriately?

5. **Compliance Check**:
   - Does the architecture meet stated compliance requirements?
   - Are audit trails properly configured?

PROVIDE YOUR VALIDATION:

```
ARCHITECTURE VALIDATION:

✅ APPROVED COMPONENTS:
- [List validated architecture components]

⚠️ RECOMMENDATIONS:
- [Suggested improvements or alternatives]

🚨 CONCERNS:
- [Any significant issues that need addressing]

FINAL ARCHITECTURE SUMMARY:
- [Concise summary of the final architecture]
- [Key services and their roles]
- [Critical configuration points]
```

Once validated, confirm you're ready to generate the production-ready CloudFormation template.
"""

    def _create_generation_prompt(self, context):
        """Final stage: Generate the actual CloudFormation template"""
        
        validated_spec = context.get("validated_spec", "")
        
        return f"""
You are an expert AWS Solutions Architect creating a production-ready CloudFormation template.

VALIDATED ARCHITECTURE SPECIFICATION:
{validated_spec}

YOUR TASK: Create a comprehensive, production-ready CloudFormation template.

TEMPLATE REQUIREMENTS:

1. **Structure**:
   - AWSTemplateFormatVersion: '2010-09-09'
   - Comprehensive Description
   - Well-documented Parameters with constraints
   - Conditions for environment-specific logic
   - All necessary Resources with proper dependencies
   - Meaningful Outputs

2. **Best Practices**:
   - Use Ref and GetAtt functions appropriately
   - Implement proper resource dependencies
   - Include comprehensive resource tags
   - Use parameter validation and constraints
   - Include condition logic for flexibility

3. **Security**:
   - Implement least privilege IAM policies
   - Enable encryption where applicable
   - Configure security groups with minimal access
   - Include CloudTrail and monitoring

4. **Documentation**:
   - Inline comments explaining complex logic
   - Parameter descriptions
   - Output descriptions
   - Deployment instructions

DELIVERABLES:

1. **Complete CloudFormation Template** (YAML format)
2. **Parameter File Example** with sample values
3. **Deployment Instructions** with CLI commands
4. **Architecture Diagram Description** (text-based)
5. **Post-Deployment Checklist**

Generate the complete, production-ready solution now.
"""