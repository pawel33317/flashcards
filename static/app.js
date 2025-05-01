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
    displaySetStats(sets);
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
        translationDiv.textContent = `Tłumaczenie: ${card.word_en}`; // Display translation
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

document.addEventListener("DOMContentLoaded", fetchSets);