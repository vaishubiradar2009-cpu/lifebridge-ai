document.addEventListener("DOMContentLoaded", () => {

    // ==================================================
    // GET ELEMENTS
    // ==================================================

    const situationInput = document.getElementById("situation");
    const contextTypeInput = document.getElementById("contextType");
    const detailLevelInput = document.getElementById("detailLevel");
    const additionalContextInput =
        document.getElementById("additionalContext");

    const analyzeBtn = document.getElementById("analyzeBtn");
    const newAnalysisBtn = document.getElementById("newAnalysisBtn");
    const newAnalysisBottomBtn =
        document.getElementById("newAnalysisBottomBtn");

    const loading = document.getElementById("loading");
    const errorBox = document.getElementById("errorBox");

    const resultsSection =
        document.getElementById("resultsSection");

    const priority =
        document.getElementById("priority");

    const confidence =
        document.getElementById("confidence");

    const priorityReason =
        document.getElementById("priorityReason");

    const situationSummary =
        document.getElementById("situationSummary");

    const factsList =
        document.getElementById("factsList");

    const verifiedList =
        document.getElementById("verifiedList");

    const needsVerificationList =
        document.getElementById("needsVerificationList");

    const actionsList =
        document.getElementById("actionsList");

    const nextAction =
        document.getElementById("nextAction");

    const whyAction =
        document.getElementById("whyAction");


    // ==================================================
    // SECURITY HELPER
    // ==================================================

    function escapeHtml(value) {

        if (value === null || value === undefined) {
            return "";
        }

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    // ==================================================
    // DISPLAY LIST
    // ==================================================

    function renderList(element, items, emptyMessage) {

        if (!element) {
            return;
        }

        element.innerHTML = "";

        if (!Array.isArray(items) || items.length === 0) {

            const li = document.createElement("li");

            li.textContent =
                emptyMessage || "No information available.";

            element.appendChild(li);

            return;
        }

        items.forEach(item => {

            const li = document.createElement("li");

            li.textContent = String(item);

            element.appendChild(li);

        });
    }


    // ==================================================
    // PRIORITY STYLE
    // ==================================================

    function setPriorityStyle(priorityValue) {

        if (!priority) {
            return;
        }

        priority.className = "priority-badge";

        const value =
            String(priorityValue || "Medium").toLowerCase();

        if (value === "urgent") {

            priority.classList.add("priority-urgent");

        } else if (value === "high") {

            priority.classList.add("priority-high");

        } else if (value === "low") {

            priority.classList.add("priority-low");

        } else {

            priority.classList.add("priority-medium");

        }
    }


    // ==================================================
    // ERROR
    // ==================================================

    function showError(message) {

        if (!errorBox) {
            return;
        }

        errorBox.textContent = message;

        errorBox.style.display = "block";
    }


    function hideError() {

        if (!errorBox) {
            return;
        }

        errorBox.textContent = "";

        errorBox.style.display = "none";
    }


    // ==================================================
    // LOADING
    // ==================================================

    function showLoading() {

        if (loading) {
            loading.style.display = "flex";
        }

        if (analyzeBtn) {

            analyzeBtn.disabled = true;

            analyzeBtn.innerHTML = `
                <span>Analyzing...</span>
                <span class="button-arrow">⏳</span>
            `;
        }
    }


    function hideLoading() {

        if (loading) {
            loading.style.display = "none";
        }

        if (analyzeBtn) {

            analyzeBtn.disabled = false;

            analyzeBtn.innerHTML = `
                <span>Analyze Situation</span>
                <span class="button-arrow">→</span>
            `;
        }
    }


    // ==================================================
    // DISPLAY RESULTS
    // ==================================================

    function displayResults(data) {

        if (!resultsSection) {
            return;
        }

        // Priority
        const priorityValue =
            data.priority || "Medium";

        priority.textContent = priorityValue;

        setPriorityStyle(priorityValue);


        // Confidence
        const confidenceValue =
            Number(data.confidence);

        if (Number.isFinite(confidenceValue)) {

            confidence.textContent =
                `${Math.max(
                    0,
                    Math.min(
                        100,
                        Math.round(confidenceValue)
                    )
                )}%`;

        } else {

            confidence.textContent = "—";

        }


        // Priority reason
        priorityReason.textContent =
            data.priority_reason ||
            "Priority is based on the information provided.";


        // Summary
        situationSummary.textContent =
            data.situation_summary ||
            "No summary was generated.";


        // Facts
        renderList(
            factsList,
            data.facts,
            "No specific facts were identified."
        );


        // Supported information
        renderList(
            verifiedList,
            data.verified,
            "No supported information was identified."
        );


        // Needs verification
        renderList(
            needsVerificationList,
            data.needs_verification,
            "No additional verification was identified."
        );


        // Actions
        renderList(
            actionsList,
            data.actions,
            "No actions were generated."
        );


        // Next action
        nextAction.textContent =
            data.next_action ||
            "Review the situation and choose the safest appropriate next step.";


        // Why action
        whyAction.textContent =
            data.why_action ||
            "This recommendation is based on the information provided.";


        // Show results
        resultsSection.style.display = "block";


        // Show new analysis button
        if (newAnalysisBtn) {
            newAnalysisBtn.style.display = "inline-flex";
        }


        // Scroll to results
        setTimeout(() => {

            resultsSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 150);
    }


    // ==================================================
    // RESET FORM
    // ==================================================

    function startNewAnalysis() {

        // Clear inputs
        if (situationInput) {
            situationInput.value = "";
        }

        if (additionalContextInput) {
            additionalContextInput.value = "";
        }


        // Reset dropdowns
        if (contextTypeInput) {
            contextTypeInput.value = "General";
        }

        if (detailLevelInput) {
            detailLevelInput.value = "Simple";
        }


        // Clear results
        if (priority) {
            priority.textContent = "Medium";
            setPriorityStyle("Medium");
        }

        if (confidence) {
            confidence.textContent = "—";
        }

        if (priorityReason) {
            priorityReason.textContent =
                "Priority is based on the information provided.";
        }

        if (situationSummary) {
            situationSummary.textContent =
                "Your situation summary will appear here.";
        }

        renderList(
            factsList,
            [],
            "No specific facts were identified."
        );

        renderList(
            verifiedList,
            [],
            "No supported information was identified."
        );

        renderList(
            needsVerificationList,
            [],
            "No additional verification was identified."
        );

        renderList(
            actionsList,
            [],
            "No actions were generated."
        );

        if (nextAction) {
            nextAction.textContent =
                "Your next best action will appear here.";
        }

        if (whyAction) {
            whyAction.textContent =
                "The reasoning will appear here.";
        }


        // Hide results
        if (resultsSection) {
            resultsSection.style.display = "none";
        }


        // Hide new analysis button
        if (newAnalysisBtn) {
            newAnalysisBtn.style.display = "none";
        }


        // Hide errors
        hideError();


        // Scroll to builder
        const builderSection =
            document.querySelector(".builder-section");

        if (builderSection) {

            builderSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }


        // Focus input
        setTimeout(() => {

            if (situationInput) {
                situationInput.focus();
            }

        }, 500);
    }


    // ==================================================
    // ANALYZE SITUATION
    // ==================================================

    if (analyzeBtn) {

        analyzeBtn.addEventListener(
            "click",
            async () => {

                hideError();


                const situation =
                    situationInput
                        ? situationInput.value.trim()
                        : "";


                const contextType =
                    contextTypeInput
                        ? contextTypeInput.value
                        : "General";


                const detailLevel =
                    detailLevelInput
                        ? detailLevelInput.value
                        : "Simple";


                const additionalContext =
                    additionalContextInput
                        ? additionalContextInput.value.trim()
                        : "";


                // Validation
                if (!situation) {

                    showError(
                        "Please describe the situation before analyzing it."
                    );

                    if (situationInput) {
                        situationInput.focus();
                    }

                    return;
                }


                if (situation.length < 10) {

                    showError(
                        "Please provide a little more detail so LifeBridge can understand the situation."
                    );

                    if (situationInput) {
                        situationInput.focus();
                    }

                    return;
                }


                showLoading();


                try {

                    const response =
                        await fetch(
                            "/api/analyze",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({

                                    situation:
                                        situation,

                                    context_type:
                                        contextType,

                                    detail_level:
                                        detailLevel,

                                    additional_context:
                                        additionalContext

                                })
                            }
                        );


                    let data;


                    try {

                        data =
                            await response.json();

                    } catch (jsonError) {

                        throw new Error(
                            "The server returned an invalid response."
                        );

                    }


                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        throw new Error(
                            data.message ||
                            "LifeBridge could not analyze the situation."
                        );

                    }


                    displayResults(data);

                } catch (error) {

                    console.error(
                        "LifeBridge error:",
                        error
                    );


                    showError(
                        error.message ||
                        "Something went wrong. Please make sure the server is running."
                    );

                } finally {

                    hideLoading();

                }

            }
        );

    }


    // ==================================================
    // NEW ANALYSIS BUTTONS
    // ==================================================

    if (newAnalysisBtn) {

        newAnalysisBtn.addEventListener(
            "click",
            startNewAnalysis
        );

    }


    if (newAnalysisBottomBtn) {

        newAnalysisBottomBtn.addEventListener(
            "click",
            startNewAnalysis
        );

    }


    // ==================================================
    // CTRL + ENTER
    // ==================================================

    if (situationInput) {

        situationInput.addEventListener(
            "keydown",
            event => {

                if (
                    event.ctrlKey &&
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    if (analyzeBtn) {
                        analyzeBtn.click();
                    }

                }

            }
        );

    }


    // ==================================================
    // INITIAL STATE
    // ==================================================

    hideError();


    if (loading) {
        loading.style.display = "none";
    }


    if (resultsSection) {
        resultsSection.style.display = "none";
    }


    if (newAnalysisBtn) {
        newAnalysisBtn.style.display = "none";
    }

});
