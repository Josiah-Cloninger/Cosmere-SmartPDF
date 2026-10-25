(function (doc) {
    // During validation, event.value contains the new Presence value.
    var presence = Number(event.value);

// calculate spiritual defense
    var awarenessField = doc.getField("Awareness.Page 1");
    var defenseField = doc.getField("Spiritual Defense");

    if (!awarenessField || !defenseField) {
        app.alert(
            "Cannot calculate Spiritual Defense: " +
            "check the Awareness and Spiritual Defense field names."
        );
        return;
    }

    var awareness = Number(awarenessField.valueAsString);

    if (!isFinite(presence) || !isFinite(awareness)) {
        return;
    }

    defenseField.value = 10 + presence + awareness;



// calculate investiture
    if (presence > awareness) {
        doc.getField("Investiture Maximum 4").value = 2 + presence;
    } 
    
})(this);