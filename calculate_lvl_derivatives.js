(function (doc) {
    // During validation, event.value contains the new Level value.
    var level = Number(event.value);

// calculate health
    var strength = Number(doc.getField("Strength.Page 1").valueAsString);
    var healthField = doc.getField("Health Maximum");

    if (1 <= level && level <= 5) {
        healthField.value = (5 * level) + 5 + strength;
    } else if (6 <= level && level <= 10) {
        healthField.value = (4 * (level - 5)) + (2 * strength) + 30;
    } else if (11 <= level && level <= 15) {
        healthField.value = (3 * (level - 10)) + (3 * strength) + 50;
    } else if (16 <= level && level <= 20) {
        healthField.value = (2 * (level - 15)) + (4 * strength) + 65;
    } else if (21 <= level) {
        healthField.value = (1 * (level - 20)) + (4 * strength) + 75;
    }
})(this);