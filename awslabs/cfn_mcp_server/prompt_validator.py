"""
Prompt Quality Validation System for CloudFormation MCP
"""

class PromptValidator:
    def __init__(self):
        self.validation_criteria = {
            "completeness": {
                "required_sections": [
                    "architecture requirements",
                    "security requirements", 
                    "operational requirements",
                    "deliverables"
                ],
                "weight": 0.3
            },
            "specificity": {
                "specific_indicators": [
                    "specific service names",
                    "configuration parameters",
                    "performance metrics",
                    "compliance standards"
                ],
                "weight": 0.25
            },
            "actionability": {
                "actionable_indicators": [
                    "step-by-step instructions",
                    "specific CLI commands",
                    "configuration examples",
                    "validation procedures"
                ],
                "weight": 0.25
            },
            "context_awareness": {
                "context_indicators": [
                    "user's specific requirements",
                    "detected architecture patterns",
                    "implicit requirements",
                    "constraint considerations"
                ],
                "weight": 0.2
            }
        }
    
    def validate_prompt_quality(self, prompt: str, context: dict) -> dict:
        """Validate the quality of a generated prompt."""
        
        scores = {}
        total_score = 0
        feedback = []
        
        # Check completeness
        completeness_score = self._check_completeness(prompt)
        scores["completeness"] = completeness_score
        total_score += completeness_score * self.validation_criteria["completeness"]["weight"]
        
        if completeness_score < 0.8:
            feedback.append("Prompt is missing key sections - add more comprehensive requirements")
        
        # Check specificity
        specificity_score = self._check_specificity(prompt, context)
        scores["specificity"] = specificity_score
        total_score += specificity_score * self.validation_criteria["specificity"]["weight"]
        
        if specificity_score < 0.7:
            feedback.append("Prompt needs more specific technical details and service configurations")
        
        # Check actionability
        actionability_score = self._check_actionability(prompt)
        scores["actionability"] = actionability_score
        total_score += actionability_score * self.validation_criteria["actionability"]["weight"]
        
        if actionability_score < 0.7:
            feedback.append("Prompt needs more actionable instructions and concrete examples")
        
        # Check context awareness
        context_score = self._check_context_awareness(prompt, context)
        scores["context_awareness"] = context_score
        total_score += context_score * self.validation_criteria["context_awareness"]["weight"]
        
        if context_score < 0.7:
            feedback.append("Prompt should better incorporate user's specific context and requirements")
        
        return {
            "overall_score": total_score,
            "component_scores": scores,
            "feedback": feedback,
            "quality_level": self._get_quality_level(total_score),
            "improvement_suggestions": self._generate_improvement_suggestions(scores, context)
        }
    
    def _check_completeness(self, prompt: str) -> float:
        """Check if prompt covers all necessary sections."""
        
        prompt_lower = prompt.lower()
        required_sections = self.validation_criteria["completeness"]["required_sections"]
        
        found_sections = 0
        for section in required_sections:
            if section in prompt_lower:
                found_sections += 1
        
        # Additional completeness checks
        completeness_indicators = [
            "parameters", "outputs", "resources", "security", "monitoring",
            "backup", "scaling", "networking", "iam", "encryption"
        ]
        
        found_indicators = sum(1 for indicator in completeness_indicators if indicator in prompt_lower)
        indicator_score = min(found_indicators / len(completeness_indicators), 1.0)
        
        section_score = found_sections / len(required_sections)
        
        return (section_score * 0.6) + (indicator_score * 0.4)
    
    def _check_specificity(self, prompt: str, context: dict) -> float:
        """Check how specific and detailed the prompt is."""
        
        prompt_lower = prompt.lower()
        
        # Check for specific AWS services mentioned
        aws_services = [
            "ec2", "s3", "rds", "lambda", "api gateway", "cloudfront", "route53",
            "alb", "elb", "vpc", "iam", "kms", "dynamodb", "kinesis", "sqs", "sns"
        ]
        
        mentioned_services = sum(1 for service in aws_services if service in prompt_lower)
        service_score = min(mentioned_services / 5, 1.0)  # Normalize to max 5 services
        
        # Check for specific configuration parameters
        config_indicators = [
            "instance type", "storage size", "memory", "cpu", "port", "protocol",
            "cidr", "subnet", "availability zone", "region", "encryption key"
        ]
        
        config_mentions = sum(1 for config in config_indicators if config in prompt_lower)
        config_score = min(config_mentions / len(config_indicators), 1.0)
        
        # Check for performance metrics
        performance_indicators = [
            "requests per second", "concurrent users", "latency", "throughput",
            "storage capacity", "bandwidth", "iops", "connections"
        ]
        
        perf_mentions = sum(1 for perf in performance_indicators if perf in prompt_lower)
        perf_score = min(perf_mentions / 4, 1.0)
        
        return (service_score * 0.4) + (config_score * 0.4) + (perf_score * 0.2)
    
    def _check_actionability(self, prompt: str) -> float:
        """Check how actionable and practical the prompt is."""
        
        prompt_lower = prompt.lower()
        
        # Check for step-by-step instructions
        instruction_indicators = [
            "step 1", "step 2", "first", "then", "next", "finally",
            "create", "configure", "deploy", "validate", "test"
        ]
        
        instruction_count = sum(1 for indicator in instruction_indicators if indicator in prompt_lower)
        instruction_score = min(instruction_count / 8, 1.0)
        
        # Check for CLI commands
        cli_indicators = ["aws ", "cloudformation", "describe-", "create-", "update-", "delete-"]
        cli_count = sum(1 for cli in cli_indicators if cli in prompt_lower)
        cli_score = min(cli_count / 5, 1.0)
        
        # Check for examples and templates
        example_indicators = ["example", "template", "sample", "format:", "```"]
        example_count = sum(1 for example in example_indicators if example in prompt_lower)
        example_score = min(example_count / 3, 1.0)
        
        return (instruction_score * 0.4) + (cli_score * 0.3) + (example_score * 0.3)
    
    def _check_context_awareness(self, prompt: str, context: dict) -> float:
        """Check how well the prompt incorporates user context."""
        
        prompt_lower = prompt.lower()
        
        # Check if user's architecture type is properly addressed
        arch_type = context.get("architecture_type", "")
        if arch_type and arch_type in prompt_lower:
            arch_score = 1.0
        else:
            arch_score = 0.5
        
        # Check if compliance requirements are addressed
        compliance_reqs = context.get("compliance_requirements", [])
        compliance_score = 0
        if compliance_reqs:
            mentioned_compliance = sum(1 for req in compliance_reqs if req in prompt_lower)
            compliance_score = mentioned_compliance / len(compliance_reqs)
        else:
            compliance_score = 1.0  # No requirements to check
        
        # Check if scale considerations are included
        scale = context.get("scale", "")
        scale_indicators = ["scale", "performance", "traffic", "load", "capacity"]
        scale_mentions = sum(1 for indicator in scale_indicators if indicator in prompt_lower)
        scale_score = min(scale_mentions / 3, 1.0)
        
        # Check if implicit requirements are addressed
        implicit_reqs = context.get("implicit_requirements", {})
        implicit_score = 0
        if implicit_reqs:
            total_implicit = sum(len(reqs) for reqs in implicit_reqs.values())
            if total_implicit > 0:
                # Check if security, performance, operational aspects are covered
                covered_aspects = 0
                if "security" in prompt_lower: covered_aspects += 1
                if "performance" in prompt_lower: covered_aspects += 1
                if "operational" in prompt_lower or "monitoring" in prompt_lower: covered_aspects += 1
                implicit_score = covered_aspects / 3
        else:
            implicit_score = 1.0
        
        return (arch_score * 0.3) + (compliance_score * 0.3) + (scale_score * 0.2) + (implicit_score * 0.2)
    
    def _get_quality_level(self, score: float) -> str:
        """Determine quality level based on score."""
        
        if score >= 0.9:
            return "EXCELLENT"
        elif score >= 0.8:
            return "GOOD"
        elif score >= 0.7:
            return "ACCEPTABLE"
        elif score >= 0.6:
            return "NEEDS_IMPROVEMENT"
        else:
            return "POOR"
    
    def _generate_improvement_suggestions(self, scores: dict, context: dict) -> list:
        """Generate specific suggestions for improving the prompt."""
        
        suggestions = []
        
        if scores["completeness"] < 0.8:
            suggestions.append(
                "Add more comprehensive sections covering security, monitoring, backup, and operational requirements"
            )
        
        if scores["specificity"] < 0.7:
            suggestions.append(
                "Include more specific AWS service configurations, instance types, and performance parameters"
            )
        
        if scores["actionability"] < 0.7:
            suggestions.append(
                "Add step-by-step instructions, CLI commands, and concrete examples"
            )
        
        if scores["context_awareness"] < 0.7:
            arch_type = context.get("architecture_type", "")
            if arch_type:
                suggestions.append(
                    f"Better incorporate {arch_type} architecture-specific requirements and best practices"
                )
            
            compliance_reqs = context.get("compliance_requirements", [])
            if compliance_reqs:
                suggestions.append(
                    f"Address {', '.join(compliance_reqs)} compliance requirements more thoroughly"
                )
        
        return suggestions
    
    def enhance_prompt_based_on_validation(self, prompt: str, validation_result: dict, context: dict) -> str:
        """Enhance a prompt based on validation feedback."""
        
        if validation_result["quality_level"] in ["EXCELLENT", "GOOD"]:
            return prompt  # Already good enough
        
        enhancement_prompt = f"""
PROMPT QUALITY ANALYSIS:
- Overall Score: {validation_result['overall_score']:.2f}
- Quality Level: {validation_result['quality_level']}

IMPROVEMENT NEEDED:
{chr(10).join(f"- {suggestion}" for suggestion in validation_result['improvement_suggestions'])}

ORIGINAL PROMPT:
{prompt}

Please enhance this prompt to address the identified weaknesses while maintaining its core structure and intent.
Focus on making it more comprehensive, specific, and actionable.
"""
        
        return enhancement_prompt