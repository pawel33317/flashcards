// frontend/app.js

let currentSetId = null;
let flashcards = [];
let currentCardIndex = 0;

async function fetchSets() {
    const response = await fetch("/api/sets");
    const sets = await response.json();
    const setSelect = document.getElementById("set-select");
    setSelect.innerHTML = sets.map(set => `<option value="${set.id}">${set.name}</option>`).join("");
    if (sets.length > 0) {
        currentSetId = sets[0].id;
        loadFlashcards();
    }

    const userResponse = await fetch("/auth/user");
    if (!userResponse.ok) {
        displayStatsNote(); // Display note if the user is not logged in
        return;
    } else {
        const user = await userResponse.json();
        const userStatsResponse = await fetch(`/api/sets?user=${user.email}`);
        const userStats = await userStatsResponse.json();
        displaySetStats(userStats); // Display stats for the logged-in user
    }
}

async function displayStatsNote() {
    const statsContainer = document.getElementById("set-stats");
    statsContainer.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr; gap: 10px; max-width: 600px; margin: 0 auto; font-weight: bold;">
            <span>Zaloguj się żeby widzieć historię i statystyki</span>
        </div>
    `;
}

async function displaySetStats(sets) {
    const statsContainer = document.getElementById("set-stats");
    statsContainer.innerHTML = `
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 10px; max-width: 600px; margin: 0 auto; font-weight: bold;">
            <span>Zestaw</span>
            <span>Słowa</span>
            <span>Znam</span>
            <span>Nie znam</span>
            <span>Nowe</span>
        </div>
    `;
    for (const set of sets) {
        statsContainer.innerHTML += `
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 10px; max-width: 600px; margin: 0 auto;">
                <span><b>${set.name}</b></span>
                <span>${set.total}</span>
                <span>${set.known}</span>
                <span>${set.unknown}</span>
                <span>${set.new}</span>
            </div>
        `;
    }
}

async function loadFlashcards() {
    const setSelect = document.getElementById("set-select");
    currentSetId = setSelect.value;
    const response = await fetch(`/api/flashcards?set_id=${currentSetId}`);
    flashcards = await response.json();
    currentCardIndex = 0;
    updateFlashcardCount(); // Update the count display
    showCard();
    disableAnswerButtons();
}

function updateFlashcardCount() {
    const remaining = flashcards.length;
    document.getElementById("set-title").textContent = `Pozostało słówek: ${remaining}`;
}

function showCard() {
    const cardDiv = document.getElementById("card");
    const translationDiv = document.getElementById("translation");
    if (flashcards.length === 0) {
        cardDiv.textContent = "Brak fiszek w tym zestawie.";
        translationDiv.textContent = ""; // Clear translation
        translationDiv.classList.remove("visible"); // Hide translation
    } else {
        const card = flashcards[currentCardIndex];
        cardDiv.textContent = card.word_pl;
        translationDiv.textContent = ""; // Clear translation
        translationDiv.classList.remove("visible"); // Hide translation
    }
}

function showTranslation() {
    if (flashcards.length > 0) {
        const card = flashcards[currentCardIndex];
        const translationDiv = document.getElementById("translation");
        translationDiv.textContent = `${card.word_en}`; // Display translation
        translationDiv.classList.add("visible"); // Add class to make it visible
        enableAnswerButtons();
        readAloud(card.word_en); // Read the English word aloud
    }
}

function readAloud(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US"; // Set language to English
    speechSynthesis.speak(utterance);
}

async function markKnown(known) {
    if (flashcards.length > 0) {
        const card = flashcards[currentCardIndex];
        await fetch("/api/stats", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ card_id: card.id, known }),
        });
        flashcards.splice(currentCardIndex, 1);
        if (currentCardIndex >= flashcards.length) {
            currentCardIndex = 0;
        }
        updateFlashcardCount(); // Update the count after answering
        showCard();
        disableAnswerButtons();
    }
}

function disableAnswerButtons() {
    document.querySelector('button[onclick="markKnown(true)"]').disabled = true;
    document.querySelector('button[onclick="markKnown(false)"]').disabled = true;
}

function enableAnswerButtons() {
    document.querySelector('button[onclick="markKnown(true)"]').disabled = false;
    document.querySelector('button[onclick="markKnown(false)"]').disabled = false;
}

async function fetchUser() {
    const response = await fetch("/auth/user");
    if (response.ok) {
        const user = await response.json();
        const loginButton = document.querySelector(".google-login");
        loginButton.textContent = `Zalogowany jako: ${user.email}`;
        loginButton.href = "#"; // Disable the login link

        // Add logout button
        const logoutButton = document.createElement("a");
        logoutButton.textContent = "Wyloguj";
        logoutButton.classList.add("logout-button");
        logoutButton.href = "#"; // Prevent default link behavior
        logoutButton.onclick = (event) => {
            event.preventDefault(); // Prevent default link behavior
            logoutUser(); // Call the logout function
        };
        loginButton.parentNode.insertBefore(logoutButton, loginButton.nextSibling); // Place it after the login button
    }
}

function logoutUser() {
    fetch("/auth/logout", { method: "POST" })
        .then(() => {
            // Refresh the page to reflect the logout state
            location.reload();
        })
        .catch((error) => {
            console.error("Logout failed:", error);
        });
}

document.addEventListener("DOMContentLoaded", () => {
    fetchSets();
    fetchUser(); // Fetch user info on page load
});

document.addEventListener("keydown", (event) => {
    const knownButton = document.querySelector('button[onclick="markKnown(true)"]');
    const unknownButton = document.querySelector('button[onclick="markKnown(false)"]');

    if (event.code === "Space") {
        event.preventDefault(); // Prevent default spacebar behavior (e.g., scrolling)
        showTranslation(); // Trigger the "Pokaż tłumaczenie" button functionality
    } else if (event.code === "Digit1" && !knownButton.disabled) {
        event.preventDefault(); // Prevent default behavior
        markKnown(true); // Trigger the "Znam" button functionality
    } else if (event.code === "Digit2" && !unknownButton.disabled) {
        event.preventDefault(); // Prevent default behavior
        markKnown(false); // Trigger the "Nie znam" button functionality
    }
});