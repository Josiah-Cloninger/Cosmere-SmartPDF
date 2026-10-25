(function (doc) {
    // During validation, event.value contains the new Awareness value.
    var awareness = Number(event.value);

// calculate spiritual defense
    var presenceField = doc.getField("Presence.Page 1");
    var defenseField = doc.getField("Spiritual Defense");

    if (!presenceField || !defenseField) {
        app.alert(
            "Cannot calculate Spiritual Defense: " +
            "check the Presence and Spiritual Defense field names."
        );
        return;
    }

    var presence = Number(presenceField.valueAsString);

    if (!isFinite(awareness) || !isFinite(presence)) {
        return;
    }

    defenseField.value = 10 + awareness + presence;


// calculate senses range
    var sensesRangeField = doc.getField("Senses Range");
    if (awareness === 0) {
        sensesRangeField.value = "5 ft.";;
    } else if (awareness === 1 || awareness === 2) {
        sensesRangeField.value = "10 ft.";;
    } else if (awareness === 3 || awareness === 4) {
        sensesRangeField.value = "20 ft.";;
    } else if (awareness === 5 || awareness === 6) {
        sensesRangeField.value = "50 ft.";;
    } else if (awareness === 7 || awareness === 8) {
        sensesRangeField.value = "100 ft.";;
    } else if (awareness >= 9) {
        sensesRangeField.value = "Unaffected by obscurred senses";;
    }

// calculate investiture
    if (awareness > presence) {
        doc.getField("Investiture Maximum 4").value = 2 + awareness;
    } 
    
})(this);