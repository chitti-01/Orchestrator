from orchestrator.analysis.requirements import TaskRequirements
from orchestrator.analysis.requirement_analyzer import RequirementAnalyzer

class DeterministicAnalyzer:
    """
    Sub-10ms requirement extraction engine wrapper leveraging RequirementAnalyzer.
    Enforces strict DOMAIN != COMPLEXITY and Intent/Action extraction.
    """
    def __init__(self):
        self.req_analyzer = RequirementAnalyzer()

    def analyze(self, prompt: str) -> TaskRequirements:
        reqs, _ = self.req_analyzer.extract_requirements(prompt)
        return reqs
