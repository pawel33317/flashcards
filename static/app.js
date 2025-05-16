// frontend/app.js

let currentSetId = null;
let flashcards = [];
let currentCardIndex = 0;
let revertEnable = false;
let translactionAlreadyShown = false;

async function fetchSets() {
    const response = await fetch("/api/sets");
    const sets = await response.json();
    const setSelect = document.getElementById("set-select");
    setSelect.innerHTML = sets.map(set => `<option value="${set.id}">${set.name}</option>`).join("");

    const savedSetId = localStorage.getItem("selectedSetId");
    if (savedSetId) {
        currentSetId = savedSetId;
        setSelect.value = savedSetId;
    } else if (sets.length > 0) {
        currentSetId = sets[0].id;
        setSelect.value = sets[0].id;
    }

    setSelect.addEventListener("change", () => {
        localStorage.setItem("selectedSetId", setSelect.value);
        loadFlashcards();
        displayStats();
    });

    if (sets.length > 0) {
        currentSetId = sets[0].id;
        loadFlashcards();
    }
    displayStats();

}
async function displayStats() {
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
    const savedSetId = localStorage.getItem("selectedSetId");
    if (savedSetId) {
        sets.sort((a, b) => {
            if (a.id == savedSetId) return -1;
            if (b.id == savedSetId) return 1;
            return 0;
        });
    }
    const statsContainer = document.getElementById("set-stats");
    statsContainer.innerHTML = `
        <div style="display: grid; grid-template-columns: 3fr 1fr 1fr 1fr 1fr 1fr; gap: 10px; max-width: 600px; margin: 0 auto; font-weight: bold;">
            <span>Zestaw</span>
            <span>Słowa</span>
            <span>Znam</span>
            <span>Nie znam</span>
            <span>Nowe</span>
            <span>Opcje</span>
        </div>
    `;
    for (const set of sets) {
        statsContainer.innerHTML += `
            <div style="display: grid; grid-template-columns: 3fr 1fr 1fr 1fr 1fr 1fr; gap: 10px; max-width: 600px; margin: 0 auto;">
                <span><b>${set.name}</b></span>
                <span>${set.total}</span>
                <span>${set.known}</span>
                <span>${set.unknown}</span>
                <span>${set.new}</span>
                <span><a href="" id="reset_set" onclick="resetSet(${set.id})" >Reset</a></span>
            </div>
        `;
    }
}

async function resetSet(id) {
    const response = await fetch(`/api/resetSet?set_id=${id}`);
    if (response.ok) {
        fetchSets()
    } else {
        alert("Nie można zresetować zestawu.");
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

function revert(){
    revertEnable = !revertEnable;
    const revertButton = document.querySelector(".revert-button");
    revertButton.textContent = revertEnable ? "Pokaż polski" : "Pokaż angielski";
    fetchSets();
}

function updateFlashcardCount() {
    const remaining = flashcards.length;
    document.getElementById("set-title").textContent = `Pozostało słówek: ${remaining}`;
}

function showCard() {
    translactionAlreadyShown = false;
    const cardDiv = document.getElementById("card");
    const translationDiv = document.getElementById("translation");
    const customTranslationInput = document.querySelector("#custom-translation input");
    customTranslationInput.value = ""; // Clear the input field
    customTranslationInput.classList.remove('match', 'no-match');
    customTranslationInput.classList.add('empty');

    if (flashcards.length === 0) {
        cardDiv.textContent = "Brak fiszek w tym zestawie.";
        translationDiv.textContent = ""; // Clear translation
        translationDiv.classList.remove("visible"); // Hide translation
    } else {
        const card = flashcards[currentCardIndex];
        if (revertEnable) {
            cardDiv.textContent = card.word_en; // Show English word first
        } else {
            cardDiv.textContent = card.word_pl; // Show Polish word first
        }
        translationDiv.textContent = ""; // Clear translation
        translationDiv.classList.remove("visible"); // Hide translation
    }

    customTranslationInput.focus(); // Set focus on the input field
}

function showTranslation() {
    translactionAlreadyShown = true;
    if (flashcards.length > 0) {
        const card = flashcards[currentCardIndex];
        const translationDiv = document.getElementById("translation");
        if (revertEnable) {
            translationDiv.textContent = `${card.word_pl}`; // Display translation
        } else {
            translationDiv.textContent = `${card.word_en}`; // Display translation
        }
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
    document.querySelector('button[onclick="markKnown(1)"]').disabled = true;
    document.querySelector('button[onclick="markKnown(-1)"]').disabled = true;
    document.querySelector('button[onclick="markKnown(-2)"]').disabled = true;
}

function enableAnswerButtons() {
    document.querySelector('button[onclick="markKnown(1)"]').disabled = false;
    document.querySelector('button[onclick="markKnown(-1)"]').disabled = false;
    document.querySelector('button[onclick="markKnown(-2)"]').disabled = false;
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
    const knownButton = document.querySelector('button[onclick="markKnown(1)"]');
    const maybeButton = document.querySelector('button[onclick="markKnown(-1)"]');
    const unknownButton = document.querySelector('button[onclick="markKnown(-2)"]');

    if (event.code === "Enter") {
        event.preventDefault(); // Prevent default spacebar behavior (e.g., scrolling)
        showTranslation(); // Trigger the "Pokaż tłumaczenie" button functionality
    } else if (event.code === "Digit1" && !unknownButton.disabled) {
        event.preventDefault(); // Prevent default behavior
        markKnown(-2); // Trigger the "Znam" button functionality
    } else if (event.code === "Digit2" && !maybeButton.disabled) {
        event.preventDefault(); // Prevent default behavior
        markKnown(-1); // Trigger the "Nie znam" button functionality
    } else if (event.code === "Digit3" && !knownButton.disabled) {
        event.preventDefault(); // Prevent default behavior
        markKnown(1); // Trigger the "Nie znam" button functionality
    }
});

document.querySelector('#custom-translation input').addEventListener('input', function() {
    const inputField = this;
    let inputValue = inputField.value;
    const card = flashcards[currentCardIndex];

    // Replace all incorrect '[' characters with the corresponding characters from the card
    const activeWord = revertEnable ? card.word_pl : card.word_en;
    let correctedValue = '';
    for (let i = 0; i < inputValue.length && i < activeWord.length; i++) {
        if (inputValue[inputValue.length-1] === '\\' || inputValue[inputValue.length-1] === '[' || inputValue[inputValue.length-1] === ']') {
            correctedValue += activeWord[i];
        } else {
            correctedValue += inputValue[i];
        }
    }
    inputValue = correctedValue;

    // Special case: if user types ' am' but the correct answer is ''m' at the same position, auto-correct it
    if (inputValue.endsWith(' am')) {
        const idx = inputValue.length - 3; // index where ' am' starts
        if (activeWord.slice(idx, idx + 2) === "'m") {
            inputValue = inputValue.slice(0, idx) + "'m";
        }
    }
    if (inputValue.endsWith(' will')) {
        const idx = inputValue.length - 5; // index where ' am' starts
        if (activeWord.slice(idx, idx + 3) === "'ll") {
            inputValue = inputValue.slice(0, idx) + "'ll";
        }
    }
    if (inputValue.endsWith(' is')) {
        const idx = inputValue.length - 3; // index where ' am' starts
        if (activeWord.slice(idx, idx + 2) === "'s") {
            inputValue = inputValue.slice(0, idx) + "'s";
        }
    }
    if (inputValue.endsWith(' not')) {    // doesn't   does not
        const idx = inputValue.length - 4; // index where ' am' starts
        if (activeWord.slice(idx, idx + 3) === "n't") {
            inputValue = inputValue.slice(0, idx) + "n't";
        }
    }
    // Zamiana małej litery na dużą jeśli w tłumaczeniu jest duża
    let finalValue = '';
    for (let i = 0; i < inputValue.length && i < activeWord.length; i++) {
        if (
            inputValue[i] &&
            inputValue[i].toLowerCase() === activeWord[i].toLowerCase() &&
            inputValue[i] !== activeWord[i]
        ) {
            finalValue += activeWord[i];
        } else {
            finalValue += inputValue[i];
        }
    }
    inputValue = finalValue;
    // Special case: if only one character left to enter and it's '?', auto-complete it
    if (inputValue.length === activeWord.length - 1 && activeWord.endsWith('?')) {
        inputValue = inputValue + '?';
    }
    if (inputValue.length === activeWord.length - 1 && activeWord.endsWith('!')) {
        inputValue = inputValue + '!';
    }
    if (inputValue.length === activeWord.length - 1 && activeWord.endsWith('.')) {
        inputValue = inputValue + '.';
    }
    inputField.value = inputValue; // Update the input field

    if (!inputValue) {
        inputField.classList.remove('match', 'no-match');
        inputField.classList.add('empty');
    } else {
        if (activeWord.toLowerCase().startsWith(inputValue.toLowerCase())) {
            inputField.classList.remove('empty', 'no-match');
            inputField.classList.add('match');
            if (inputValue.toLowerCase() === activeWord.toLowerCase() && !translactionAlreadyShown) {
                showTranslation();
            }
        } else {
            inputField.classList.remove('empty', 'match');
            inputField.classList.add('no-match');
        }
    }
});