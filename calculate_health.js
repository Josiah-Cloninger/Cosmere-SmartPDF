(function (doc) {  
    var levelField = doc.getField("Level.Page 1");
    var strengthField = doc.getField("Strength.Page 1");
    var healthField = doc.getField("Health Maximum");
    var hardyTraitField = doc.getField("Has Hardy Trait");

    // Stop if any required field is missing.
    if (!levelField || !strengthField || !healthField || !hardyTraitField) {
        app.alert(
            "Cannot calculate health. Check these field names:\n" +
            "Level.Page 1\n" +
            "Strength.Page 1\n" +
            "Health Maximum\n" +
            "Has Hardy Trait"
        );
        return;
    }

    // Start with the values currently stored in the PDF.
    var level = Number(levelField.valueAsString);
    var strength = Number(strengthField.valueAsString);

    // Identify which field triggered this script.
    // For example, "Strength.Page 2" becomes "Strength".
    var sourceName = event.target.name.replace(/\.Page \d+$/, "");

    // During validation, the edited field's new value is in event.value.
    // Other fields can still contain the previous, stored value.
    if (sourceName === "Level") {
        level = Number(event.value);
    } else if (sourceName === "Strength") {
        strength = Number(event.value);
    }

    // Require a positive whole-number Level and a numeric Strength.
    if (
        !isFinite(level) ||
        level < 1 ||
        Math.floor(level) !== level ||
        !isFinite(strength)
    ) {
        return;
    }

    // Calculate base maximum health in a local variable.
    var health;

    if (level <= 5) {
        health = (5 * level) + 5 + strength;
    } else if (level <= 10) {
        health = (4 * (level - 5)) + (2 * strength) + 30;
    } else if (level <= 15) {
        health = (3 * (level - 10)) + (3 * strength) + 50;
    } else if (level <= 20) {
        health = (2 * (level - 15)) + (4 * strength) + 65;
    } else {
        health = (level - 20) + (4 * strength) + 75;
    }

    // Hardy adds health equal to Level.
    if (hardyTraitField.isBoxChecked(0)) {
        health += level;
    }

    // Write the completed result once.
    healthField.value = health;
})(this);