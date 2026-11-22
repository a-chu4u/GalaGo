
document.addEventListener("DOMContentLoaded", function () {

    function setupSpotDetailButton() {
        const match = window.location.pathname.match(
            /^\/spots\/(\d+)\/$/
        );

        if (!match) return;

        const title = document.querySelector(".spot-title");
        if (!title) return;

        const button = document.createElement("a");

        button.href = "/itinerary/?spot=" +
            encodeURIComponent(match[1]);

        button.className = "spot-itinerary-btn";
        button.textContent = "＋ Add to Itinerary";

        Object.assign(button.style, {
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "12px 18px",
            border: "1.5px solid #244b38",
            borderRadius: "999px",
            background: "#ffffff",
            color: "#244b38",
            fontSize: "14px",
            fontWeight: "700",
            textDecoration: "none"
        });

        const row = document.querySelector(".spot-title-row");

        if (row) {
            row.appendChild(button);
        } else {
            title.insertAdjacentElement("afterend", button);
            button.style.marginBottom = "16px";
        }
    }

    setupSpotDetailButton();

    const planner = document.getElementById(
        "itinerary-planner"
    );

    if (!planner) return;

    const API_URL = planner.dataset.apiUrl || "/itinerary/data/";

    const form = document.getElementById("planner-form");
    const spotSelect = document.getElementById("planner-spot");
    const dateInput = document.getElementById("planner-date");
    const timeInput = document.getElementById("planner-time");
    const durationInput = document.getElementById("planner-duration");
    const costInput = document.getElementById("planner-cost");
    const notesInput = document.getElementById("planner-notes");

    const list = document.getElementById("planner-list");
    const empty = document.getElementById("planner-empty");
    const count = document.getElementById("planner-count");
    const daysCount = document.getElementById("planner-days");
    const budgetTotal = document.getElementById("planner-budget");

    const message = document.getElementById("planner-message");
    const saveButton = document.getElementById("planner-save");
    const cancelButton = document.getElementById("planner-cancel");
    const formHeading = document.getElementById(
        "planner-form-heading"
    );

    let plans = [];
    let editingId = null;

    function getCookie(name) {
        for (const cookie of document.cookie.split(";")) {
            const trimmed = cookie.trim();

            if (trimmed.startsWith(name + "=")) {
                return decodeURIComponent(
                    trimmed.slice(name.length + 1)
                );
            }
        }

        return "";
    }

    async function apiRequest(url, options = {}) {
        const method = options.method || "GET";

        const response = await fetch(url, {
            ...options,
            method,
            credentials: "same-origin",
            headers: {
                Accept: "application/json",

                ...(method !== "GET" ? {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                } : {}),

                ...(options.headers || {})
            }
        });

        if (response.redirected) {
            throw new Error(
                "Your session expired. Please log in again."
            );
        }

        const type = response.headers.get(
            "content-type"
        ) || "";

        if (!type.includes("application/json")) {
            throw new Error("Unexpected server response.");
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Unable to complete request."
            );
        }

        return data;
    }

    function textElement(tag, className, value) {
        const el = document.createElement(tag);

        if (className) {
            el.className = className;
        }

        el.textContent = value;
        return el;
    }

    function money(value) {
        return "₱" + Number(value || 0).toLocaleString(
            "en-PH",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }
        );
    }

    function dateLabel(value) {
        const [y, m, d] = value.split("-").map(Number);

        return new Date(
            y,
            m - 1,
            d
        ).toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric"
        });
    }

    function timeLabel(value) {
        if (!value) return "";

        const [hours, minutes] = value.split(":").map(Number);

        const hour12 = hours % 12 || 12;

        return hour12 + ":" +
            String(minutes).padStart(2, "0") +
            (hours >= 12 ? " PM" : " AM");
    }

    function durationLabel(value) {
        if (value === "" || value == null) return "";

        const hours = Number(value);
        const totalMinutes = Math.round(hours * 60);
        const wholeHours = Math.floor(totalMinutes / 60);
        const remainingMinutes = totalMinutes % 60;

        const parts = [];

        if (wholeHours) {
            parts.push(
                wholeHours + (
                    wholeHours === 1 ? " hour" : " hours"
                )
            );
        }

        if (remainingMinutes) {
            parts.push(
                remainingMinutes + " min"
            );
        }

        return parts.join(" ") || "0 min";
    }

    function spotName(id) {
        const option = Array.from(
            spotSelect.options
        ).find(
            o => o.value === String(id)
        );

        return option
            ? option.textContent.trim()
            : "Destination unavailable";
    }

    function resetForm() {
        form.reset();
        editingId = null;

        formHeading.textContent = "Add a Destination";
        saveButton.textContent = "Save to Itinerary";
        cancelButton.hidden = true;
    }

    function renderPlans() {
        const sorted = [...plans].sort(
            (a, b) =>
                a.visitDate.localeCompare(b.visitDate) ||
                (a.visitTime || "99:99").localeCompare(
                    b.visitTime || "99:99"
                ) ||
                Number(a.id) - Number(b.id)
        );

        list.replaceChildren();

        count.textContent = sorted.length +
            (
                sorted.length === 1
                    ? " planned visit"
                    : " planned visits"
            );

        empty.hidden = sorted.length !== 0;

        const groups = new Map();

        for (const plan of sorted) {
            if (!groups.has(plan.visitDate)) {
                groups.set(plan.visitDate, []);
            }

            groups.get(plan.visitDate).push(plan);
        }

        daysCount.textContent = String(groups.size);

        const totalCents = sorted.reduce(
            (sum, p) =>
                sum + Math.round(
                    Number(p.estimatedCost || 0) * 100
                ),
            0
        );

        budgetTotal.textContent = money(totalCents / 100);

        let dayIndex = 0;

        for (const [day, dayPlans] of groups) {
            dayIndex++;

            const section = textElement(
                "section",
                "planner-day",
                ""
            );

            const heading = textElement(
                "div",
                "planner-day-heading",
                ""
            );

            heading.appendChild(
                textElement(
                    "h3",
                    "",
                    "Day " + dayIndex +
                    " — " + dateLabel(day)
                )
            );

            const dayCents = dayPlans.reduce(
                (sum, p) =>
                    sum + Math.round(
                        Number(p.estimatedCost || 0) * 100
                    ),
                0
            );

            heading.appendChild(
                textElement(
                    "span",
                    "",
                    "Day budget: " + money(dayCents / 100)
                )
            );

            section.appendChild(heading);

            for (const plan of dayPlans) {
                const card = textElement(
                    "article",
                    "planner-item",
                    ""
                );

                card.appendChild(
                    textElement(
                        "h4",
                        "",
                        spotName(plan.spotId)
                    )
                );

                const meta = textElement(
                    "div",
                    "planner-meta",
                    ""
                );

                if (plan.visitTime) {
                    meta.appendChild(
                        textElement(
                            "span",
                            "planner-pill",
                            "🕒 " + timeLabel(plan.visitTime)
                        )
                    );
                }

                if (
                    plan.durationHours !== "" &&
                    plan.durationHours != null
                ) {
                    meta.appendChild(
                        textElement(
                            "span",
                            "planner-pill",
                            "⏳ " + durationLabel(
                                plan.durationHours
                            )
                        )
                    );
                }

                if (
                    plan.estimatedCost !== "" &&
                    plan.estimatedCost != null
                ) {
                    meta.appendChild(
                        textElement(
                            "span",
                            "planner-pill",
                            "💰 " + money(plan.estimatedCost)
                        )
                    );
                }

                card.appendChild(meta);

                if (plan.notes) {
                    const notes = textElement(
                        "p",
                        "",
                        plan.notes
                    );

                    notes.style.whiteSpace = "pre-line";
                    card.appendChild(notes);
                }

                const actions = textElement(
                    "div",
                    "planner-actions",
                    ""
                );

                const link = textElement(
                    "a",
                    "planner-small-btn",
                    "View Destination"
                );

                link.href = "/spots/" +
                    encodeURIComponent(plan.spotId) + "/";

                actions.appendChild(link);

                const edit = textElement(
                    "button",
                    "planner-small-btn",
                    "Edit"
                );

                edit.type = "button";

                edit.addEventListener(
                    "click",
                    () => startEditing(plan.id)
                );

                actions.appendChild(edit);

                const remove = textElement(
                    "button",
                    "planner-small-btn planner-delete",
                    "Delete"
                );

                remove.type = "button";

                remove.addEventListener(
                    "click",
                    () => deletePlan(plan.id)
                );

                actions.appendChild(remove);

                card.appendChild(actions);
                section.appendChild(card);
            }

            list.appendChild(section);
        }
    }

    function startEditing(id) {
        const plan = plans.find(
            p => p.id === String(id)
        );

        if (!plan) return;

        editingId = plan.id;

        spotSelect.value = plan.spotId;
        dateInput.value = plan.visitDate;
        timeInput.value = plan.visitTime || "";
        durationInput.value = plan.durationHours ?? "";
        costInput.value = plan.estimatedCost ?? "";
        notesInput.value = plan.notes || "";

        formHeading.textContent = "Edit Travel Plan";
        saveButton.textContent = "Update Itinerary";
        cancelButton.hidden = false;

        message.textContent = "";

        document.getElementById(
            "planner-form-section"
        ).scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    async function loadPlans() {
        try {
            const data = await apiRequest(API_URL);

            plans = data.plans;
            renderPlans();

            return true;
        } catch (error) {
            count.textContent =
                "Unable to load travel plans.";

            message.textContent = error.message;
            return false;
        }
    }

    async function deletePlan(id) {
        if (!window.confirm(
            "Remove this destination from your itinerary?"
        )) {
            return;
        }

        try {
            await apiRequest(
                API_URL + encodeURIComponent(id) + "/",
                { method: "DELETE" }
            );

            if (editingId === id) {
                resetForm();
            }

            if (await loadPlans()) {
                message.textContent =
                    "Travel plan removed successfully.";
            }
        } catch (error) {
            message.textContent = error.message;
        }
    }

    form.addEventListener(
        "submit",
        async function (event) {
            event.preventDefault();

            if (!form.reportValidity()) return;

            const wasEditing = editingId !== null;

            const url = wasEditing
                ? API_URL +
                  encodeURIComponent(editingId) + "/"
                : API_URL;

            saveButton.disabled = true;

            message.textContent =
                "Saving your travel plan...";

            try {
                await apiRequest(url, {
                    method: wasEditing ? "PUT" : "POST",

                    body: JSON.stringify({
                        spotId: spotSelect.value,
                        visitDate: dateInput.value,
                        visitTime: timeInput.value,
                        durationHours: durationInput.value,
                        estimatedCost: costInput.value,
                        notes: notesInput.value.trim()
                    })
                });

                resetForm();

                if (await loadPlans()) {
                    message.textContent = wasEditing
                        ? "Travel plan updated successfully!"
                        : "Destination added to your itinerary!";
                }
            } catch (error) {
                message.textContent = error.message;
            } finally {
                saveButton.disabled = false;
            }
        }
    );

    cancelButton.addEventListener(
        "click",
        function () {
            resetForm();
            message.textContent = "";
        }
    );

    const requestedSpot = new URLSearchParams(
        window.location.search
    ).get("spot");

    if (
        requestedSpot &&
        Array.from(spotSelect.options).some(
            o => o.value === requestedSpot
        )
    ) {
        spotSelect.value = requestedSpot;
    }

    loadPlans();
});
