(function (doc) {
    // During validation, event.value contains the new Willpower value.
    var willpower = Number(event.value);

// calculate cognitive defense
    var intellectField = doc.getField("Intellect.Page 1");
    var defenseField = doc.getField("Cognitive Defense");

    if (!intellectField || !defenseField) {
        app.alert(
            "Cannot calculate Cognitive Defense: " +
            "check the Intellect and Cognitive Defense field names."
        );
        return;
    }

    var intellect = Number(intellectField.valueAsString);

    if (!isFinite(willpower) || !isFinite(intellect)) {
        return;
    }

    defenseField.value = 10 + willpower + intellect;


// calculate recovery die
    var recoveryDieField = doc.getField("Recovery Die");
    if (willpower === 0) {
        recoveryDieField.value = "1d4";;
    } else if (willpower === 1 || willpower === 2) {
        recoveryDieField.value = "1d6";;
    } else if (willpower === 3 || willpower === 4) {
        recoveryDieField.value = "1d8";;
    } else if (willpower === 5 || willpower === 6) {
        recoveryDieField.value = "1d10";;
    } else if (willpower === 7 || willpower === 8) {
        recoveryDieField.value = "1d12";;
    } else if (willpower >= 9) {
        recoveryDieField.value = "1d20";;
    }

// calculate focus
    doc.getField("Focus Maximum").value = 2 + willpower;
    
})(this);