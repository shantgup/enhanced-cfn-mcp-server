"""
Intelligent Question Generation for CloudFormation Requirements Discovery
"""

class IntelligentQuestionGenerator:
    def __init__(self):
        self.question_templates = {
            "architecture_disambiguation": {
                "web_application": [
                    "When you say 'web application', do you mean:",
                    "  a) A static website with CDN",
                    "  b) A dynamic web app with backend API", 
                    "  c) A full-stack application with database",
                    "  d) A microservices-based web platform"
                ],
                "data_processing": [
                    "For data processing, are you looking for:",
                    "  a) Real-time stream processing (Kinesis)",
                    "  b) Batch processing jobs (EMR/Glue)",
                    "  c) ETL pipelines with scheduling",
                    "  d) Analytics and reporting platform"
                ],
                "microservices": [
                    "For microservices architecture, do you need:",
                    "  a) Container orchestration (ECS/EKS)",
                    "  b) Serverless functions (Lambda)",
                    "  c) Service mesh capabilities",
                    "  d) API gateway and service discovery"
                ]
            },
            
            "scale_discovery": {
                "traffic_patterns": [
                    "What's your expected traffic pattern?",
                    "  - Requests per second (peak/average)",
                    "  - Concurrent users",
                    "  - Data volume processed",
                    "  - Geographic distribution"
                ],
                "growth_expectations": [
                    "How do you expect usage to grow?",
                    "  - Current vs 6-month projection",
                    "  - Seasonal traffic variations", 
                    "  - Expected user base growth",
                    "  - Data growth rate"
                ]
            },
            
            "integration_discovery": {
                "existing_systems": [
                    "What existing systems need integration?",
                    "  - Databases (type, location, size)",
                    "  - APIs (internal/external)",
                    "  - Authentication systems",
                    "  - Monitoring/logging tools"
                ],
                "data_sources": [
                    "What are your data sources and destinations?",
                    "  - Input data formats and sources",
                    "  - Output requirements",
                    "  - Data transformation needs",
                    "  - Real-time vs batch requirements"
                ]
            },
            
            "constraints_discovery": {
                "compliance_requirements": [
                    "Do you have compliance requirements?",
                    "  - HIPAA (healthcare data)",
                    "  - PCI-DSS (payment data)",
                    "  - GDPR (EU personal data)",
                    "  - SOX (financial reporting)",
                    "  - Industry-specific regulations"
                ],
                "operational_constraints": [
                    "What are your operational constraints?",
                    "  - Budget limitations",
                    "  - Maintenance windows",
                    "  - Skill set of operations team",
                    "  - Preferred AWS services/regions"
                ]
            }
        }
    
    def generate_targeted_questions(self, analysis_result: dict) -> dict:
        """Generate intelligent questions based on analysis results."""
        
        questions = {
            "critical": [],      # Must answer for good template
            "important": [],     # Should answer for better template  
            "optional": []       # Nice to have for optimal template
        }
        
        architecture_type = analysis_result.get("architecture_type", "general")
        confidence = analysis_result.get("architecture_confidence", 0)
        conflicts = analysis_result.get("conflicts", [])
        implicit_reqs = analysis_result.get("implicit_requirements", {})
        
        # Critical questions for low confidence or conflicts
        if confidence < 0.7 or conflicts:
            questions["critical"].extend(
                self._generate_disambiguation_questions(architecture_type, conflicts)
            )
        
        # Always ask about scale - it's critical for good architecture
        questions["critical"].extend(
            self._generate_scale_questions(analysis_result)
        )
        
        # Important questions about integration and constraints
        questions["important"].extend(
            self._generate_integration_questions(architecture_type)
        )
        
        questions["important"].extend(
            self._generate_constraint_questions(analysis_result)
        )
        
        # Optional questions for optimization
        questions["optional"].extend(
            self._generate_optimization_questions(architecture_type, implicit_reqs)
        )
        
        return questions
    
    def _generate_disambiguation_questions(self, primary_type: str, conflicts: list) -> list:
        """Generate questions to resolve architecture ambiguity."""
        
        questions = []
        
        if primary_type in self.question_templates["architecture_disambiguation"]:
            questions.extend(
                self.question_templates["architecture_disambiguation"][primary_type]
            )
        
        if conflicts:
            questions.append(
                f"I detected multiple possible architectures: {', '.join(conflicts)}. "
                f"Which best describes what you're building?"
            )
        
        return questions
    
    def _generate_scale_questions(self, analysis: dict) -> list:
        """Generate questions about scale and performance requirements."""
        
        questions = []
        
        # Always ask about scale - it's fundamental to good architecture
        questions.extend([
            "What's your expected scale?",
            "  - How many users/requests per day?",
            "  - Peak vs average load?", 
            "  - Data volume processed?",
            "  - Geographic distribution of users?"
        ])
        
        # Architecture-specific scale questions
        arch_type = analysis.get("architecture_type", "")
        
        if arch_type == "web_application":
            questions.extend([
                "For your web application:",
                "  - Concurrent users expected?",
                "  - Page load time requirements?",
                "  - Database query volume?"
            ])
        elif arch_type == "data_processing":
            questions.extend([
                "For data processing:",
                "  - Data volume per hour/day?",
                "  - Processing latency requirements?",
                "  - Batch vs real-time processing?"
            ])
        
        return questions
    
    def _generate_integration_questions(self, architecture_type: str) -> list:
        """Generate questions about system integration needs."""
        
        base_questions = [
            "What systems does this need to integrate with?",
            "  - Existing databases or data stores",
            "  - External APIs or services", 
            "  - Authentication/authorization systems",
            "  - Monitoring and logging tools"
        ]
        
        # Add architecture-specific integration questions
        if architecture_type == "microservices":
            base_questions.extend([
                "For microservices integration:",
                "  - How many services initially?",
                "  - Service communication patterns?",
                "  - Shared data requirements?"
            ])
        elif architecture_type == "data_processing":
            base_questions.extend([
                "For data integration:",
                "  - Data source formats and locations?",
                "  - Output destinations and formats?",
                "  - Data transformation requirements?"
            ])
        
        return base_questions
    
    def _generate_constraint_questions(self, analysis: dict) -> list:
        """Generate questions about constraints and requirements."""
        
        questions = [
            "What are your key constraints?",
            "  - Budget limitations or cost targets",
            "  - Compliance requirements (HIPAA, PCI, etc.)",
            "  - Performance requirements (latency, throughput)",
            "  - Availability requirements (uptime, RTO/RPO)"
        ]
        
        # Add compliance-specific questions if detected
        compliance_reqs = analysis.get("compliance_requirements", [])
        if compliance_reqs:
            questions.extend([
                f"I detected potential {', '.join(compliance_reqs)} requirements.",
                "Please confirm:",
                "  - Specific compliance standards needed",
                "  - Data classification levels",
                "  - Audit and reporting requirements"
            ])
        
        return questions
    
    def _generate_optimization_questions(self, architecture_type: str, implicit_reqs: dict) -> list:
        """Generate questions for optimization opportunities."""
        
        questions = [
            "For optimization, consider:",
            "  - Preferred AWS services or constraints",
            "  - Disaster recovery requirements",
            "  - Monitoring and alerting preferences",
            "  - Automation and CI/CD integration"
        ]
        
        # Add questions based on implicit requirements
        if implicit_reqs.get("performance"):
            questions.extend([
                "Performance optimization:",
                "  - Caching requirements",
                "  - Auto-scaling preferences", 
                "  - Database performance needs"
            ])
        
        if implicit_reqs.get("security"):
            questions.extend([
                "Security considerations:",
                "  - Data encryption requirements",
                "  - Network isolation needs",
                "  - Access control preferences"
            ])
        
        return questions
    
    def create_discovery_prompt_with_questions(self, user_request: str, analysis: dict) -> str:
        """Create a comprehensive discovery prompt with intelligent questions."""
        
        questions = self.generate_targeted_questions(analysis)
        
        prompt = f"""
You are an expert AWS Solutions Architect conducting a requirements discovery session.

USER REQUEST: "{user_request}"

INITIAL ANALYSIS:
- Detected Architecture: {analysis.get('architecture_type', 'Unknown')} 
- Confidence: {analysis.get('architecture_confidence', 0)*100:.0f}%
- Potential Conflicts: {analysis.get('conflicts', [])}
- Compliance Indicators: {analysis.get('compliance_requirements', [])}

INTELLIGENT DISCOVERY QUESTIONS:

🔴 CRITICAL (Must Answer):
"""
        
        for question in questions["critical"]:
            prompt += f"{question}\n"
        
        prompt += f"""
🟡 IMPORTANT (Should Answer):
"""
        
        for question in questions["important"]:
            prompt += f"{question}\n"
        
        prompt += f"""
🟢 OPTIONAL (For Optimization):
"""
        
        for question in questions["optional"]:
            prompt += f"{question}\n"
        
        prompt += f"""

RESPONSE FORMAT:
Please answer the CRITICAL questions first, then as many IMPORTANT questions as possible.

```
CRITICAL ANSWERS:
[Your answers to critical questions]

IMPORTANT ANSWERS: 
[Your answers to important questions]

ADDITIONAL CONTEXT:
[Any other relevant information]
```

Based on your answers, I'll create a comprehensive architecture specification and CloudFormation template.
"""
        
        return prompt