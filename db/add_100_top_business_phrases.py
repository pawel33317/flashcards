import sqlite3

conn = sqlite3.connect("flashcards.db")
cursor = conn.cursor()

# Przykładowe zestawy i fiszki
sets = [
    ("Top 100 Business phrases",),  # Ensure each entry is a tuple
]

cursor.executemany("INSERT INTO sets (name) VALUES (?)", sets)

# Pobierz ID zestawu "Top 100 Phrasal Verbs"
cursor.execute("SELECT id FROM sets WHERE name = ?", sets[0])
set_id = cursor.fetchone()[0]

flashcards = [
("nawiąż kontakt", "get in touch", set_id),
("skontaktuj się", "reach out", set_id),
("zadzwoń do mnie", "ping me", set_id),
("prześlij mi maila", "shoot me an email", set_id),
("będziemy w kontakcie", "keep me in the loop", set_id),
("włącz mnie do korespondencji", "loop me in", set_id),
("odpisz jak najszybciej", "respond ASAP", set_id),
("daj znać", "let me know", set_id),
("prześlij informację zwrotną", "follow up", set_id),
("odpisz mi", "get back to me", set_id),
("daj mi znać", "drop me a line", set_id),
("nie wahaj się skontaktować", "don't hesitate to contact me", set_id),
("chętnie podtrzymam kontakt", "feel free to connect", set_id),
("znajdziesz mnie pod numerem", "reach me at", set_id),
("zadzwoń później", "call me back", set_id),
("ustalmy termin spotkania", "let's connect", set_id),
("omówmy to później", "circle back", set_id),
("skontaktuję się z tobą", "I'll get in touch", set_id),
("omawiamy dalej", "let's touch base", set_id),
("bądź na bieżąco", "stay tuned", set_id),
("umów spotkanie", "schedule a meeting", set_id),
("zwołaj spotkanie", "call a meeting", set_id),
("rozpocznij spotkanie", "kick off", set_id),
("ustaw porządek obrad", "set the agenda", set_id),
("podsumujmy", "wrap up", set_id),
("skończmy na dziś", "call it a day", set_id),
("oto najważniejsze punkty", "action items", set_id),
("trzymajmy się harmonogramu", "time is of the essence", set_id),
("wszyscy na pokład", "all hands on deck", set_id),
("czas twarzą w twarz", "face time", set_id),
("zgodzimy się co do...", "on the same page", set_id),
("zróbmy burzę mózgów", "brainstorm", set_id),
("zagłębmy się w szczegóły", "deep dive", set_id),
("przeprowadź warsztat", "workshop", set_id),
("zrób notatki", "minute the meeting", set_id),
("przeanalizujmy to offline", "take it offline", set_id),
("ustawmy wideokonferencję", "set up a video call", set_id),
("zaproszę wszystkich", "invite everyone", set_id),
("omówimy to później", "table this for now", set_id),
("spotkajmy się w cztery oczy", "one-on-one", set_id),
("rozpocznijmy realizację", "get the ball rolling", set_id),
("przesuń wskaźnik", "move the needle", set_id),
("myśl nieszablonowo", "think outside the box", set_id),
("zmień kierunek", "pivot", set_id),
("przeprowadź analizę SWOT", "conduct a SWOT analysis", set_id),
("zrób due diligence", "do due diligence", set_id),
("przygotuj plan działania", "draft a roadmap", set_id),
("zapewnij skalowalność", "ensure scalability", set_id),
("wyznacz kamienie milowe", "set milestones", set_id),
("optymalizuj procesy", "streamline processes", set_id),
("wykorzystaj zasoby", "leverage resources", set_id),
("ustal priorytety", "prioritize tasks", set_id),
("przewiduj ryzyka", "anticipate risks", set_id),
("zoptymalizuj koszty", "optimize costs", set_id),
("przejdź do kolejnego etapu", "take it to the next level", set_id),
("przygotuj biznesowy case", "build a business case", set_id),
("zmniejsz liczbę błędów", "reduce errors", set_id),
("przygotuj się na przyszłość", "plan ahead", set_id),
("utrzymaj konkurencyjność", "stay ahead of the curve", set_id),
("zrób prognozę", "make a forecast", set_id),
("podejmij decyzję", "make a decision", set_id),
("rozważ opcje", "weigh the options", set_id),
("uzyskaj akceptację", "get sign-off", set_id),
("zamknij temat", "close the loop", set_id),
("przekaż informację zwrotną", "give feedback", set_id),
("prześlij aktualizację statusu", "provide a status update", set_id),
("przypomnienie", "heads up", set_id),
("wyślij informacje", "send the details", set_id),
("ustal termin wykonania", "set a deadline", set_id),
("zleć wykonanie", "delegate the task", set_id),
("bądź odpowiedzialny", "take ownership", set_id),
("rozlicz się z wyników", "report back", set_id),
("podsumuj wnioski", "debrief", set_id),
("przeanalizuj wyniki", "review the outcomes", set_id),
("zamknij raport", "finalize the report", set_id),
("wdróż rekomendacje", "implement recommendations", set_id),
("narysuj wnioski", "draw conclusions", set_id),
("zaplanuj kolejny krok", "plan the next step", set_id),
("udokumentuj proces", "document the process", set_id),
("naucz się na błędach", "capture lessons learned", set_id),
("daj z siebie więcej", "go the extra mile", set_id),
("ponad oczekiwania", "above and beyond", set_id),
("sytuacja korzystna dla obu stron", "win-win situation", set_id),
("współdziałanie", "synergy", set_id),
("ogranicz zasoby", "manage bandwidth", set_id),
("szybkie zwycięstwo", "quick win", set_id),
("łatwy cel", "low-hanging fruit", set_id),
("przełomowy pomysł", "game changer", set_id),
("kluczowe wskaźniki", "key performance indicators", set_id),
("zwrot z inwestycji", "return on investment", set_id),
("gotowe rezultaty", "deliverables", set_id),
("kamienie milowe", "milestones", set_id),
("budżet", "budget", set_id),
("przegląd wydajności", "performance review", set_id),
("nagradzaj sukcesy", "recognize achievements", set_id),
("zmierz postępy", "track progress", set_id),
("trzymaj się kryteriów", "adhere to guidelines", set_id),
("ucząca się organizacja", "learning organization", set_id),
("motywuj zespół", "motivate the team", set_id),
("zapewnij wsparcie", "provide support", set_id),
]

cursor.executemany("INSERT INTO flashcards (word_pl, word_en, set_id) VALUES (?, ?, ?)", flashcards)

conn.commit()
conn.close()

print("Baza danych została zaktualizowana i wypełniona przykładowymi danymi.")