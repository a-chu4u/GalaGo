
document.addEventListener("DOMContentLoaded", function () {

    const STORAGE_KEY = "galago_itinerary";

    function getPlans() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            const parsed = raw ? JSON.parse(raw) : [];

            if (!Array.isArray(parsed)) {
                return [];
            }

            return parsed.filter(function (plan) {
                return (
                    plan &&
                    typeof plan === "object" &&
                    typeof plan.spotId === "string" &&
                    typeof plan.visitDate === "string" &&
                    typeof plan.id === "string"
                );
            });

        } catch (error) {
            return [];
        }
    }

    function savePlans(plans) {
        try {
            localStorage.setItem(
                STORAGE_KEY,
                JSON.stringify(plans)
            );
            return true;
        } catch (error) {
            return false;
        }
    }

    function createId() {
        if (
            typeof crypto !== "undefined" &&
            typeof crypto.randomUUID === "function"
        ) {
            return crypto.randomUUID();
        }

        return (
            Date.now().toString(36) +
            "-" +
            Math.random().toString(36).slice(2)
        );
    }

    function formatDate(dateString) {
        const parts = dateString.split("-");

        if (parts.length !== 3) {
            return dateString;
        }

        const year = Number(parts[0]);
        const month = Number(parts[1]);
        const day = Number(parts[2]);

        const date = new Date(year, month - 1, day);

        if (
            date.getFullYear() !== year ||
            date.getMonth() !== month - 1 ||
            date.getDate() !== day
        ) {
            return dateString;
        }

        return date.toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric"
        });
    }

    // ADD BUTTON TO TOURIST SPOT DETAIL PAGE

    function setupSpotDetailButton() {
        const match = window.location.pathname.match(
            /^\/spots\/(\d+)\/$/
        );

        if (!match) {
            return;
        }

        const title = document.querySelector(".spot-title");

        if (!title) {
            return;
        }

        const spotId = match[1];

        const button = document.createElement("a");

        button.href =
            "/itinerary/?spot=" + encodeURIComponent(spotId);

        button.className = "spot-itinerary-btn";

        button.textContent = "＋ Add to Itinerary";

        button.style.display = "inline-flex";
        button.style.alignItems = "center";
        button.style.justifyContent = "center";
        button.style.padding = "12px 18px";
        button.style.border = "1.5px solid #244b38";
        button.style.borderRadius = "999px";
        button.style.background = "#ffffff";
        button.style.color = "#244b38";
        button.style.fontSize = "14px";
        button.style.fontWeight = "700";
        button.style.textDecoration = "none";

        const titleRow = document.querySelector(
            ".spot-title-row"
        );

        if (titleRow) {
            titleRow.appendChild(button);
        } else {
            title.insertAdjacentElement(
                "afterend",
                button
            );
            button.style.marginBottom = "16px";
        }
    }

    setupSpotDetailButton();

    // TRAVEL PLANNER PAGE

    const planner = document.getElementById(
        "itinerary-planner"
    );

    if (!planner) {
        return;
    }

    const form = document.getElementById("planner-form");
    const spotSelect = document.getElementById("planner-spot");
    const dateInput = document.getElementById("planner-date");
    const notesInput = document.getElementById("planner-notes");

    const list = document.getElementById("planner-list");
    const empty = document.getElementById("planner-empty");
    const count = document.getElementById("planner-count");

    const message = document.getElementById("planner-message");
    const saveButton = document.getElementById("planner-save");
    const cancelButton = document.getElementById("planner-cancel");
    const formHeading = document.getElementById(
        "planner-form-heading"
    );

    let editingId = null;

    function getSpotName(spotId) {
        const option = Array.from(spotSelect.options).find(
            function (item) {
                return item.value === spotId;
            }
        );

        return option
            ? option.textContent.trim()
            : "Destination no longer available";
    }

    function makeTextElement(tag, className, content) {
        const element = document.createElement(tag);

        if (className) {
            element.className = className;
        }

        element.textContent = content;

        return element;
    }

    function resetForm() {
        form.reset();
        editingId = null;

        formHeading.textContent = "Add a Destination";
        saveButton.textContent = "Save to Itinerary";
        cancelButton.hidden = true;
    }

    function renderPlans() {
        const plans = getPlans().sort(function (a, b) {
            return a.visitDate.localeCompare(b.visitDate);
        });

        list.replaceChildren();

        count.textContent =
            plans.length +
            (plans.length === 1
                ? " planned visit"
                : " planned visits");

        empty.hidden = plans.length !== 0;

        plans.forEach(function (plan) {
            const card = document.createElement("article");
            card.className = "planner-item";

            const name = makeTextElement(
                "h3",
                "",
                getSpotName(plan.spotId)
            );

            const date = makeTextElement(
                "p",
                "planner-item-date",
                "📅 " + formatDate(plan.visitDate)
            );

            card.appendChild(name);
            card.appendChild(date);

            if (plan.notes) {
                const notes = makeTextElement(
                    "p",
                    "",
                    plan.notes
                );

                notes.style.whiteSpace = "pre-line";
                card.appendChild(notes);
            }

            const actions = document.createElement("div");
            actions.className = "planner-actions";

            if (
                Array.from(spotSelect.options).some(
                    function (option) {
                        return option.value === plan.spotId;
                    }
                )
            ) {
                const viewLink = document.createElement("a");

                viewLink.href = "/spots/" +
                    encodeURIComponent(plan.spotId) + "/";

                viewLink.textContent = "View Destination";
                viewLink.className = "planner-small-btn";
                viewLink.style.textDecoration = "none";

                actions.appendChild(viewLink);
            }

            const editButton = document.createElement("button");
            editButton.type = "button";
            editButton.className = "planner-small-btn";
            editButton.textContent = "Edit";

            editButton.addEventListener("click", function () {
                startEditing(plan.id);
            });

            actions.appendChild(editButton);

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.className =
                "planner-small-btn planner-delete";
            deleteButton.textContent = "Delete";

            deleteButton.addEventListener("click", function () {
                deletePlan(plan.id);
            });

            actions.appendChild(deleteButton);

            card.appendChild(actions);
            list.appendChild(card);
        });
    }

    function startEditing(planId) {
        const plan = getPlans().find(function (item) {
            return item.id === planId;
        });

        if (!plan) {
            return;
        }

        editingId = plan.id;

        spotSelect.value = plan.spotId;
        dateInput.value = plan.visitDate;
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

    function deletePlan(planId) {
        const confirmed = window.confirm(
            "Remove this destination from your itinerary?"
        );

        if (!confirmed) {
            return;
        }

        const updated = getPlans().filter(function (plan) {
            return plan.id !== planId;
        });

        if (!savePlans(updated)) {
            message.textContent =
                "Unable to update itinerary in this browser.";
            return;
        }

        if (editingId === planId) {
            resetForm();
        }

        message.textContent =
            "Travel plan removed successfully.";

        renderPlans();
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const spotId = spotSelect.value;
        const visitDate = dateInput.value;
        const notes = notesInput.value.trim();

        if (!spotId || !visitDate) {
            message.textContent =
                "Please select a destination and visit date.";
            return;
        }

        const plans = getPlans();

        if (editingId) {
            const index = plans.findIndex(function (plan) {
                return plan.id === editingId;
            });

            if (index === -1) {
                message.textContent =
                    "This travel plan no longer exists.";
                resetForm();
                renderPlans();
                return;
            }

            plans[index] = {
                ...plans[index],
                spotId: spotId,
                visitDate: visitDate,
                notes: notes
            };

        } else {
            plans.push({
                id: createId(),
                spotId: spotId,
                visitDate: visitDate,
                notes: notes
            });
        }

        if (!savePlans(plans)) {
            message.textContent =
                "Unable to save itinerary in this browser.";
            return;
        }

        const wasEditing = editingId !== null;

        resetForm();
        renderPlans();

        message.textContent = wasEditing
            ? "Travel plan updated successfully!"
            : "Destination added to your itinerary!";
    });

    cancelButton.addEventListener("click", function () {
        resetForm();
        message.textContent = "";
    });

    // PRESELECT SPOT FROM DESTINATION DETAIL PAGE

    const params = new URLSearchParams(
        window.location.search
    );

    const requestedSpot = params.get("spot");

    if (requestedSpot) {
        const available = Array.from(
            spotSelect.options
        ).some(function (option) {
            return option.value === requestedSpot;
        });

        if (available) {
            spotSelect.value = requestedSpot;
        }
    }

    // REFRESH IF ANOTHER TAB CHANGES ITINERARY

    window.addEventListener("storage", function (event) {
        if (event.key === STORAGE_KEY) {
            renderPlans();
        }
    });

    renderPlans();
});
