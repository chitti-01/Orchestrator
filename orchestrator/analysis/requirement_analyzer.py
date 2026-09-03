import re
from typing import List, Dict, Any, Tuple, Optional
from orchestrator.analysis.requirements import TaskRequirements, RequirementItem
from orchestrator.analysis.requirement_graph import RequirementGraph

class RequirementAnalyzer:
    """
    Multi-layer Requirement & Relationship Extractor for V5.
    Performs Intent, Deliverable, Scope, Constraint, Technology Exclusion, and Requirement Graph extraction.
    Strictly enforces DOMAIN != COMPLEXITY and NO TECHNOLOGY HALLUCINATION.
    """
    def __init__(self):
        # Action Verbs
        self.intent_patterns = {
            "prove": [r'\bprove\b', r'\bproof of\b', r'\btheorem\b', r'\bderive\b'],
            "audit": [r'\baudit\b', r'\bsecurity review\b', r'\bthreat model\b', r'\bvulnerability\b', r'\bpci-dss\b'],
            "design_architecture": [r'\bdesign\b', r'\barchitect\b', r'\bplatform architecture\b', r'\bdistributed system\b', r'\bdistributed database\b', r'\bdocument-processing platform\b', r'\bcollaborative editor\b'],
            "refactor": [r'\brefactor\b', r'\boptimize\b', r'\bdebug\b', r'\bfix\b', r'\brewrite\b'],
            "build": [r'\bbuild\b', r'\bcreate\b', r'\bimplement\b', r'\bwrite a\b', r'\bdevelop\b'],
            "explain": [r'\bexplain\b', r'\bwhat is\b', r'\bhow does\b', r'\bdefine\b', r'\bdescribe\b', r'\bsummarize\b'],
            "summarize": [r'\bsummarize\b', r'\bsummary\b', r'\btldr\b']
        }

        self.medium_keywords = {
            "script", "rest api", "fastapi", "flask", "django", "express", "sql query", "window function",
            "dockerfile", "docker-compose", "dijkstra", "binary search tree", "lru cache", "regex",
            "scraper", "multi-threaded", "asyncio", "ansible", "terraform", "graphql", "pytest", "mock",
            "multiprocessing", "redis", "postgres", "mongodb", "nginx", "bash script", "trie", "websocket",
            "code examples", "algorithm", "garbage collection", "locking", "b-tree", "lsm-tree", "decorator"
        }

        # Constraint patterns & requirement item definitions
        self.constraint_patterns = {
            "globally consistent transactions": ([r'globally consistent', r'consistency', r'acid', r'serializable'], "reliability", ["architecture", "concurrency"]),
            "network partition tolerance": ([r'network partition', r'partition tolerance', r'cap theorem', r'split-brain'], "reliability", ["architecture", "reliability"]),
            "horizontal scaling": ([r'horizontal scaling', r'horizontally scale', r'sharding', r'auto-scaling'], "scale", ["architecture", "scale"]),
            "zero downtime": ([r'without downtime', r'zero downtime', r'rolling update', r'99\.99%'], "reliability", ["reliability"]),
            "regional failure recovery": ([r'regional failure', r'disaster recovery', r'multi-region', r'failover'], "reliability", ["architecture", "reliability"]),
            "concurrent write correctness": ([r'concurrent write', r'race condition', r'concurrency control', r'isolation', r'concurrent edits'], "functional", ["concurrency", "architecture"]),
            "sub-microsecond latency": ([r'sub-microsecond', r'sub-millisecond', r'low latency'], "performance", ["performance"]),
            "pci compliance": ([r'pci-dss', r'pci compliance', r'credit card security'], "security", ["security"]),
            "fault tolerance": ([r'fault-tolerant', r'fault tolerance', r'high availability'], "reliability", ["reliability", "architecture"]),
            "multi-tenant data isolation": ([r'multi-tenant', r'tenant', r'authorization', r'permission-aware'], "security", ["security", "architecture"]),
            "semantic chunking & embeddings": ([r'chunking', r'embedding', r'vector search', r'hybrid search'], "functional", ["coding", "architecture"]),
            "end-to-end testing strategy": ([r'testing strategy', r'end-to-end test', r'unit test'], "testing", ["testing"])
        }

    def extract_requirements(self, prompt: str) -> Tuple[TaskRequirements, RequirementGraph]:
        clean_prompt = prompt.strip()
        lower = clean_prompt.lower()
        words = re.findall(r'\w+', lower)
        word_count = len(words)

        is_medium_kw = any(k in lower for k in self.medium_keywords)

        # 1. Determine Intent (Enforce DOMAIN != COMPLEXITY)
        is_explain_query = (
            lower.startswith("explain ") or
            lower.startswith("what is ") or
            lower.startswith("how does ") or
            lower.startswith("describe ") or
            lower.startswith("summarize ") or
            lower.startswith("list five") or
            lower.startswith("list 5") or
            "in simple terms" in lower or
            (lower.startswith("write a short documentation") and "build" not in lower and "design" not in lower)
        ) and not (lower.startswith("design") or lower.startswith("build") or lower.startswith("implement") or lower.startswith("create"))

        if is_explain_query:
            intent = "explain"
        elif any(re.search(p, lower) for p in self.intent_patterns["prove"]) or "derive" in lower or "proof" in lower:
            intent = "prove"
        elif any(re.search(p, lower) for p in self.intent_patterns["audit"]):
            intent = "audit"
        elif any(re.search(p, lower) for p in self.intent_patterns["design_architecture"]):
            intent = "design_architecture"
        elif any(re.search(p, lower) for p in self.intent_patterns["build"]) or is_medium_kw:
            if "operating system" in lower or "distributed database" in lower or "consensus protocol" in lower or "document-processing platform" in lower or "collaborative editor" in lower:
                intent = "design_architecture"
            else:
                intent = "build"
        elif any(re.search(p, lower) for p in self.intent_patterns["refactor"]):
            intent = "refactor"
        elif any(re.search(p, lower) for p in self.intent_patterns["summarize"]):
            intent = "summarize"
        else:
            intent = "explain"

        # 2. Actionability & Single vs Multi-Task Decision
        is_actionable = intent in ["build", "design_architecture", "refactor", "audit", "prove"]
        is_simple_operation = is_explain_query or intent in ["explain", "summarize"] or any(phrase in lower for phrase in ["reverse a string", "hello world", "binary search tree", "what is a", "explain how", "summarize", "list five", "list 5"])
        can_solve_directly = (not is_actionable) or (is_simple_operation and "platform" not in lower and "distributed database" not in lower and not ("build" in lower and "collaborative" in lower))

        # 3. Technology Exclusion Extraction (Rule 10: No Technology Hallucination)
        explicit_exclusions = []
        if any(phrase in lower for phrase in ["do not assume any specific", "do not use any specific", "no specific database", "without assuming", "prohibit"]):
            explicit_exclusions.append("Prohibited assumption of unrequested cloud providers, databases, queues, or languages")

        explicit_tech = []
        for tech in ["fastapi", "react", "python", "postgres", "redis", "kafka", "docker", "kubernetes"]:
            if re.search(r'\b' + tech + r'\b', lower):
                explicit_tech.append(tech)

        # 4. Extract Explicit Requirement Items (R1..Rn)
        extracted_items: List[RequirementItem] = []
        req_graph = RequirementGraph(raw_prompt=clean_prompt)
        constraints_found = []

        req_idx = 1
        for constraint_name, (patterns, category, caps) in self.constraint_patterns.items():
            if any(re.search(p, lower) for p in patterns):
                constraints_found.append(constraint_name)
                req_id = f"R{req_idx}"
                item = RequirementItem(
                    id=req_id,
                    description=f"Requirement: {constraint_name}",
                    category=category,
                    criticality="critical" if category in ["security", "reliability"] else "high",
                    explicit=True,
                    required_capabilities=caps
                )
                extracted_items.append(item)
                req_graph.add_item(item)
                req_idx += 1

        if is_actionable and not extracted_items and not can_solve_directly:
            components = self._identify_components(lower, clean_prompt)
            for idx, comp in enumerate(components, 1):
                item = RequirementItem(
                    id=f"R{idx}",
                    description=f"Implement requirement for {comp}",
                    category="functional",
                    criticality="high",
                    explicit=True,
                    required_capabilities=["architecture" if intent == "design_architecture" else "coding"]
                )
                extracted_items.append(item)
                req_graph.add_item(item)

        # Build Requirement Graph Relationships
        item_dict = {item.description.lower(): item.id for item in extracted_items}
        if "requirement: globally consistent transactions" in item_dict and "requirement: network partition tolerance" in item_dict:
            req_graph.add_relationship(item_dict["requirement: network partition tolerance"], item_dict["requirement: globally consistent transactions"], "affects_consistency")

        # 5. Scope & Deliverable Type
        components = self._identify_components(lower, clean_prompt)
        scope = "single_operation"
        if is_actionable:
            if len(components) >= 4 or len(extracted_items) >= 4:
                scope = "complete_system"
            elif len(components) >= 2 or len(extracted_items) >= 2 or "gateway" in lower or "api" in lower:
                scope = "multiple_components"

        deliverable_type = "natural_language_answer"
        if intent == "prove":
            deliverable_type = "proof"
        elif intent == "design_architecture":
            deliverable_type = "architecture"
        elif intent in ["build", "refactor"] or is_medium_kw:
            deliverable_type = "code"

        # 6. Multi-dimensional score calculation
        if not is_actionable or can_solve_directly:
            reasoning_depth = 0.25 if intent in ["explain", "summarize"] else 0.20
            planning_req = 0.15
            impl_scope = 0.20
            arch_comp = 0.10
            dep_comp = 0.10
            sec_req = 0.10
            scale_req = 0.10
            rel_req = 0.10
            con_density = 0.10
            testing_req = 0.10
            output_comp = 0.10
        else:
            reasoning_depth = 0.95 if intent in ["prove", "design_architecture"] or "distributed" in lower else 0.65
            planning_req = 0.90 if intent == "design_architecture" or not can_solve_directly else 0.60
            impl_scope = 0.90 if scope == "complete_system" else (0.60 if scope == "multiple_components" else 0.20)
            arch_comp = 0.90 if intent == "design_architecture" or "distributed" in lower else 0.60
            dep_comp = 0.85 if not can_solve_directly else 0.15
            sec_req = 0.90 if any(c in lower for c in ["pci", "auth", "crypto", "security", "vulnerability", "fraud", "tenant"]) else 0.30
            scale_req = 0.90 if any(k in lower for k in ["distributed", "multi-region", "replication", "scaling", "concurrent"]) else 0.30
            rel_req = 0.90 if any(k in lower for k in ["fault-tolerant", "fault tolerance", "disaster recovery", "downtime", "99.99%"]) else 0.30
            con_density = 0.85 if len(constraints_found) >= 2 else 0.30
            testing_req = 0.85 if scope == "complete_system" or "compliance" in lower or "testing" in lower else 0.30
            output_comp = 0.85 if scope in ["complete_system", "multiple_components"] else 0.30

        task_reqs = TaskRequirements(
            raw_prompt=clean_prompt,
            intent=intent,
            deliverable_type=deliverable_type,
            scope=scope,
            constraints=constraints_found,
            actors_components=components,
            explicit_technologies=explicit_tech,
            recommended_technologies=[],
            explicit_exclusions=explicit_exclusions,
            implicit_dependencies=[],
            is_actionable=is_actionable,
            can_solve_directly=can_solve_directly,
            extracted_requirements=extracted_items,
            reasoning_depth=reasoning_depth,
            planning_requirement=planning_req,
            implementation_scope=impl_scope,
            architecture_complexity=arch_comp,
            dependency_complexity=dep_comp,
            security_requirement=sec_req,
            scale_requirement=scale_req,
            reliability_requirement=rel_req,
            constraint_density=con_density,
            testing_requirement=testing_req,
            output_complexity=output_comp,
            security_critical=any(c in lower for c in ["pci", "auth", "crypto", "security", "vulnerability", "tenant"]),
            system_architecture=intent == "design_architecture" or ("distributed" in lower and is_actionable),
            formal_proof=intent == "prove",
            multi_component=len(components) >= 2 or len(extracted_items) >= 2,
            component_count=max(len(components), len(extracted_items), 1),
            estimated_steps=max(len(extracted_items) + 1, 1),
            token_estimate=int(word_count * 1.3)
        )

        return task_reqs, req_graph

    def _identify_components(self, lower: str, raw: str) -> List[str]:
        components = []
        candidates = [
            "authentication", "payment gateway", "fraud detection", "database replication",
            "transaction processing", "inventory", "product catalog", "order checkout",
            "consistency strategy", "partition handling", "scaling controller", "failure recovery",
            "monitoring", "load balancer", "api layer", "document ingestion", "semantic chunking",
            "embedding generation", "hybrid retrieval", "permission-aware authorization"
        ]
        for cand in candidates:
            if cand in lower:
                components.append(cand.title())
        if not components and ("system" in lower or "platform" in lower or "gateway" in lower or "api" in lower or "editor" in lower):
            components = ["Core Engine", "Integration Layer"]
        return components
