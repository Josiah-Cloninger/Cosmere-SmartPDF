(function (doc) {
    // During validation, event.value contains the new Speed value.
    var speed = Number(event.value);

// calculate physical defense
    var strengthField = doc.getField("Strength.Page 1");
    var defenseField = doc.getField("Physical Defense");

    if (!strengthField || !defenseField) {
        app.alert(
            "Cannot calculate Physical Defense: " +
            "check the Strength and Physical Defense field names."
        );
        return;
    }

    var strength = Number(strengthField.valueAsString);

    if (!isFinite(speed) || !isFinite(strength)) {
        return;
    }

    defenseField.value = 10 + speed + strength;


// calculate movement rate
    var movementField = doc.getField("Movement");
    if (speed === 0) {
        movementField.value = "20 ft.";;
    } else if (speed === 1 || speed === 2) {
        movementField.value = "25 ft.";;
    } else if (speed === 3 || speed === 4) {
        movementField.value = "30 ft.";;
    } else if (speed === 5 || speed === 6) {
        movementField.value = "40 ft.";;
    } else if (speed === 7 || speed === 8) {
        movementField.value = "60 ft.";;
    } else if (speed >= 9) {
        movementField.value = "80 ft.";;
    }
})(this);