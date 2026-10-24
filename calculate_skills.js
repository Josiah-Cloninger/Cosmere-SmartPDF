(function (doc) {
    // Each entry: [output field, stat name, rank checkbox prefix]
    var skills = [
        ["Agility", "Speed", "Agility"],
        ["Athletics", "Strength", "Athletics"],
        ["Heavy Weapons", "Strength", "Heavy Weaponry"],
        ["Light Weapons", "Speed", "Light Weaponry"],
        ["Stealth", "Speed", "Stealth"],
        ["Thievery", "Speed", "Thievery"],

        ["Crafting", "Intellect", "Crafting"],
        ["Deduction", "Intellect", "Deduction"],
        ["Discipline", "Willpower", "Discipline"],
        ["Intimidation", "Willpower", "Intimidation"],
        ["Lore", "Intellect", "Lore"],
        ["Medicine", "Intellect", "Medicine"],

        ["Deception", "Presence", "Deception"],
        ["Insight", "Awareness", "Insight"],
        ["Leadership", "Presence", "Leadership"],
        ["Perception", "Awareness", "Perception"],
        ["Persuasion", "Presence", "Persuasion"],
        ["Survival", "Awareness", "Survival"]
    ];

    // calculate defenses
    var strengthField = doc.getField("Strength.Page 1");
    var intellectField = doc.getField("Intellect.Page 1");
    var willpowerField = doc.getField("Willpower.Page 1");
    var presenceField = doc.getField("Presence.Page 1");
    var awarenessField = doc.getField("Awareness.Page 1");

    var cognitiveDefenseField = doc.getField("Cognitive Defense.Page 1");
    var spiritualDefenseField = doc.getField("Spiritual Defense.Page 1");

    if (intellectField && willpowerField && cognitiveDefenseField) {
        var intellect = Number(intellectField.valueAsString);
        var willpower = Number(willpowerField.valueAsString);

        cognitiveDefenseField.value = 10 + intellect + willpower;
    }

    if (awarenessField && presenceField && spiritualDefenseField) {
        var awareness = Number(awarenessField.valueAsString);
        var presence = Number(presenceField.valueAsString);

        spiritualDefenseField.value = 10 + awareness + presence;
    }

    // calculate skill bonuses
    for (var i = 0; i < skills.length; i++) {
        var outputName = skills[i][0];
        var statName = skills[i][1] + ".Page 1";
        var rankPrefix = skills[i][2];

        var output = doc.getField(outputName);
        var stat = doc.getField(statName);

        if (output === null || stat === null) {
            throw new Error("Missing skill or stat field: " + outputName);
        }

        var statText = stat.valueAsString;
        var statValue = Number(statText);

        // Leave the skill blank if its stat is empty or invalid.
        if (
            statText.replace(/\s/g, "") === "" ||
            !isFinite(statValue)
        ) {
            output.value = "";
            continue;
        }

        var ranks = 0;

        for (var rank = 1; rank <= 5; rank++) {
            var checkboxName = rankPrefix + " Rank " + rank;
            var checkbox = doc.getField(checkboxName);

            if (checkbox === null) {
                throw new Error("Missing rank checkbox: " + checkboxName);
            }

            if (checkbox.isBoxChecked(0)) {
                ranks++;
            }
        }

        var total = statValue + ranks;

        if (output.valueAsString !== String(total)) {
            output.value = total;
        }
    }
})(this);