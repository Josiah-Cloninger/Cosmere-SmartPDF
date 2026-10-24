(function (doc) {
    // During validation, event.value contains the new Speed value.
    var speed = Number(event.value);

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
})(this);