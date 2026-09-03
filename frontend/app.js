document.addEventListener("DOMContentLoaded", () => {
    const promptInput = document.getElementById("promptInput");
    const executeBtn = document.getElementById("executeBtn");
    const spinner = document.getElementById("spinner");

    const valModel = document.getElementById("valModel");
    const valScore = document.getElementById("valScore");
    const valConfidence = document.getElementById("valConfidence");
    const valIntent = document.getElementById("valIntent");
    const valDeliverable = document.getElementById("valDeliverable");
    const valScope = document.getElementById("valScope");

    const exclusionsList = document.getElementById("exclusionsList");
    const extractedReqsList = document.getElementById("extractedReqsList");
    const coverageList = document.getElementById("coverageList");
    const graphContainer = document.getElementById("graphContainer");
    const auditContainer = document.getElementById("auditContainer");
    const signalsList = document.getElementById("signalsList");

    const intelToggle = document.getElementById("intelToggle");
    const intelBody = document.getElementById("intelBody");

    // Collapsible Intelligence Panel
    if (intelToggle && intelBody) {
        intelToggle.addEventListener("click", () => {
            intelBody.classList.toggle("open");
        });
    }

    // Preset Buttons
    document.querySelectorAll(".preset-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            promptInput.value = btn.getAttribute("data-prompt");
        });
    });

    executeBtn.addEventListener("click", async () => {
        const prompt = promptInput.value.trim();
        if (!prompt) return;

        spinner.classList.remove("hidden");
        executeBtn.disabled = true;

        try {
            const resp = await fetch("/api/orchestrate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: prompt })
            });

            if (!resp.ok) {
                const errData = await resp.json();
                throw new Error(errData.detail || "API execution failed");
            }

            const data = await resp.json();
            renderResults(data);
        } catch (err) {
            alert("Error: " + err.message);
        } finally {
            spinner.classList.add("hidden");
            executeBtn.disabled = false;
        }
    });

    function renderResults(data) {
        // Main Metrics
        valModel.textContent = (data.selected_model || "model_1").toUpperCase();
        valScore.textContent = `${data.workflow_complexity || data.complexity_score || 0} / 100`;
        valConfidence.textContent = data.confidence ? `${Math.round(data.confidence * 100)}%` : "95%";
        valIntent.textContent = data.task_type || "explain";
        valDeliverable.textContent = data.deliverable_type || "text";
        valScope.textContent = data.scope || "single_operation";

        // Explicit Technology Exclusions
        if (data.explicit_exclusions && data.explicit_exclusions.length > 0) {
            exclusionsList.innerHTML = data.explicit_exclusions.map(ex => 
                `<span class="badge badge-exclusion">⚠️ ${ex}</span>`
            ).join("");
        } else {
            exclusionsList.innerHTML = `<span class="no-data">None specified (Unrequested tech injections strictly prohibited by Rule 10)</span>`;
        }

        // Extracted Requirements
        if (data.extracted_requirements && data.extracted_requirements.length > 0) {
            extractedReqsList.innerHTML = data.extracted_requirements.map(req => 
                `<span class="badge badge-req">📌 [${req.id}] ${req.description} (${req.criticality})</span>`
            ).join("");
        } else {
            extractedReqsList.innerHTML = `<span class="no-data">1 Direct Task Node</span>`;
        }

        // Requirement Coverage
        if (data.requirement_coverage && data.requirement_coverage.length > 0) {
            coverageList.innerHTML = data.requirement_coverage.map(cov => 
                `<div class="cov-item ${cov.status.toLowerCase()}">
                    <span class="cov-status">${cov.status === "SATISFIED" ? "✓" : "✗"} [${cov.req_id}] ${cov.description}</span>
                    <span class="cov-evidence">${cov.evidence}</span>
                </div>`
            ).join("");
        } else {
            coverageList.innerHTML = `<span class="no-data">Coverage verified in single task execution</span>`;
        }

        // Dynamic Task Graph & Per-Task Model Assignments (V5 Card Breakdown)
        if (data.plan && data.plan.length > 0) {
            graphContainer.innerHTML = data.plan.map(node => {
                const modelTier = (node.selected_model || "model_1").toUpperCase();
                const badgeClass = modelTier === "MODEL_3" ? "badge-m3" : (modelTier === "MODEL_2" ? "badge-m2" : "badge-m1");
                const depsStr = node.dependencies && node.dependencies.length > 0 ? ` [Deps: ${node.dependencies.join(", ")}]` : " [Root]";

                // Render Required Capabilities
                let capsHtml = "";
                if (node.required_capabilities && Object.keys(node.required_capabilities).length > 0) {
                    capsHtml = Object.entries(node.required_capabilities).map(([cap, score]) => 
                        `<span class="cap-pill">${cap}: <strong>${score}</strong></span>`
                    ).join(" ");
                } else {
                    capsHtml = `<span class="cap-pill">general: 0.40</span>`;
                }

                // Render Candidate Models Status (MODEL_1, MODEL_2, MODEL_3)
                const candidates = [
                    { id: "model_1", label: "M1" },
                    { id: "model_2", label: "M2" },
                    { id: "model_3", label: "M3" }
                ];

                const candHtml = candidates.map(c => {
                    const isSelected = (node.selected_model || "").toLowerCase() === c.id;
                    const isEligible = node.eligible_models ? node.eligible_models.includes(c.id) : true;
                    const rejReason = node.rejected_models ? node.rejected_models[c.id] : "";
                    
                    let statusBadge = "";
                    if (isSelected) {
                        statusBadge = `<span class="cand-badge cand-selected">SELECTED</span>`;
                    } else if (isEligible) {
                        statusBadge = `<span class="cand-badge cand-eligible">✓ Eligible</span>`;
                    } else {
                        statusBadge = `<span class="cand-badge cand-rejected" title="${rejReason}">✕ Rejected</span>`;
                    }

                    return `<div class="cand-item ${isSelected ? 'selected' : (isEligible ? 'eligible' : 'rejected')}">
                        <span class="cand-name">${c.label}</span>
                        ${statusBadge}
                        ${rejReason ? `<span class="rej-reason">${rejReason}</span>` : ''}
                    </div>`;
                }).join("");

                return `<div class="node-card">
                    <div class="node-header">
                        <div>
                            <span class="node-title">${node.name}</span>
                            <span class="node-meta">Score: ${node.task_complexity || node.node_complexity || 20} | Criticality: ${node.criticality || 'medium'}</span>
                        </div>
                        <span class="badge ${badgeClass}">${modelTier}</span>
                    </div>
                    <p class="node-desc">${node.description}${depsStr}</p>
                    
                    <div class="node-caps-section">
                        <div class="caps-title">Required Capabilities Vector:</div>
                        <div class="caps-list">${capsHtml}</div>
                    </div>

                    <div class="node-cands-section">
                        <div class="cands-title">Candidate Models Evaluation:</div>
                        <div class="cands-grid">${candHtml}</div>
                    </div>

                    <div class="node-reason">
                        💡 <strong>Selection Reason:</strong> ${node.selection_reason || 'Lowest-cost capable model'}
                    </div>
                </div>`;
            }).join("");
        } else {
            graphContainer.innerHTML = `<span class="no-data">No plan nodes generated</span>`;
        }

        // Routing Audit Panel Table
        if (data.routing_audit && data.routing_audit.length > 0) {
            let tableHtml = `<table class="audit-table">
                <thead>
                    <tr>
                        <th>Task Name</th>
                        <th>Task Complexity</th>
                        <th>Criticality</th>
                        <th>Selected Model</th>
                        <th>Eligible Models</th>
                        <th>Rejected Models</th>
                        <th>Selection Rationale</th>
                    </tr>
                </thead>
                <tbody>`;

            data.routing_audit.forEach(item => {
                const sel = item.selected || item.selected_model.toUpperCase();
                const selBadge = sel === "MODEL_3" ? "badge-m3" : (sel === "MODEL_2" ? "badge-m2" : "badge-m1");
                const eligibleStr = item.eligible ? item.eligible.map(e => e.toUpperCase()).join(", ") : "M1, M2, M3";
                const rejectedStr = item.rejected && item.rejected.length > 0 ? item.rejected.map(r => r.toUpperCase()).join(", ") : "None";

                tableHtml += `<tr>
                    <td><strong>${item.task}</strong></td>
                    <td><span class="audit-score">${item.task_complexity || 20}</span></td>
                    <td><span class="audit-crit ${item.criticality}">${item.criticality}</span></td>
                    <td><span class="badge ${selBadge}">${sel}</span></td>
                    <td><span class="text-green">${eligibleStr}</span></td>
                    <td><span class="text-red">${rejectedStr}</span></td>
                    <td class="audit-reason">${item.reason}</td>
                </tr>`;
            });

            tableHtml += `</tbody></table>`;
            auditContainer.innerHTML = tableHtml;
        } else {
            auditContainer.innerHTML = `<span class="no-data">No routing audit generated</span>`;
        }

        // Signals List
        let signals = [];
        if (data.routing_decision && data.routing_decision.reasons && data.routing_decision.reasons.length > 0) {
            signals = data.routing_decision.reasons;
        } else {
            signals = ["Task model routing evaluated independently per node via fine-grained capability gap vectors."];
        }

        signalsList.innerHTML = signals.map(sig => `<div class="sig-item">💡 ${sig}</div>`).join("");

        if (intelBody) intelBody.classList.add("open");
    }
});
