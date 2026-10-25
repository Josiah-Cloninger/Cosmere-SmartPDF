(function (doc) {
    // During validation, event.value contains the new Intellect value.
    var intellect = Number(event.value);

// calculate cognitive defense
    var willpowerField = doc.getField("Willpower.Page 1");
    var defenseField = doc.getField("Cognitive Defense");

    if (!willpowerField || !defenseField) {
        app.alert(
            "Cannot calculate Cognitive Defense: " +
            "check the Willpower and Cognitive Defense field names."
        );
        return;
    }

    var willpower = Number(willpowerField.valueAsString);

    if (!isFinite(intellect) || !isFinite(willpower)) {
        return;
    }

    defenseField.value = 10 + intellect + willpower;
})(this);