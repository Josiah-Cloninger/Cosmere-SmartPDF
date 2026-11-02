(function (doc) {
    function getField(name) {
        var field = doc.getField(name);

        if (field === null) {
            throw new Error("Missing field: " + name);
        }

        return field;
    }

    // Identify which field triggered this script.
    // For example, "Strength.Page 2" becomes "Strength".
    var sourceName = event.target.name.replace(/\.Page \d+$/, "");

    // During validation, the edited field's new value is in event.value.
    // Other fields can still contain the previous, stored value.
    function readNumber(baseName, fieldName) {
        var text = sourceName === baseName
            ? String(event.value)
            : getField(fieldName).valueAsString;

        return text.replace(/\s/g, "") === "" ? null : Number(text);
    }

    function hasTrait(name) {
        return getField("Has " + name + " Trait").isBoxChecked(0);
    }

    var attributes = {};
    var effective = {};
    var names = [
        "Strength", "Speed", "Intellect",
        "Willpower", "Awareness", "Presence"
    ];

    for (var i = 0; i < names.length; i++) {
        var attribute = readNumber(names[i], names[i] + ".Page 1");
        var enhancedName = "Enhanced " + names[i];
        var enhanced = readNumber(enhancedName, enhancedName);

        // Leave the sheet unchanged until invalid entries are corrected.
        if (!isFinite(attribute) || !isFinite(enhanced)) {
            return;
        }

        // Blank attributes stay null so their results can be cleared.
        attributes[names[i]] = attribute;

        // Enhanced only reaches the values that use "effective" below.
        effective[names[i]] = attribute === null
            ? null
            : attribute + (enhanced || 0);
    }

    var level = readNumber("Level", "Level.Page 1");

    // Require a positive whole-number Level for level-based values.
    if (level === null || !(level >= 1) || Math.floor(level) !== level) {
        level = null;
    }

    var tier = level === null ? 0 : Math.min(Math.ceil(level / 5), 5);

    // Attribute tables share one set of score bands:
    // 0, 1-2, 3-4, 5-6, 7-8, and 9+.
    function fromTable(score, table) {
        if (score === null) {
            return "";
        }

        return table[Math.max(0, Math.min(5, Math.ceil(score / 2)))];
    }

// calculate defenses (never Enhanced)
    function setDefense(name, first, second, bonus) {
        getField(name).value = first === null && second === null
            ? ""
            : 10 + first + second + bonus;
    }

    var collected = hasTrait("Collected") ? 2 : 0;
    var garb = hasTrait("Customary Garb") ? 2 : 0;

    setDefense(
        "Physical Defense",
        attributes.Strength,
        attributes.Speed,
        garb
    );
    setDefense(
        "Cognitive Defense",
        attributes.Intellect,
        attributes.Willpower,
        collected
    );
    setDefense(
        "Spiritual Defense",
        attributes.Awareness,
        attributes.Presence,
        collected + garb
    );

// calculate maximum health (never Enhanced)
    if (level !== null) {
        var strength = attributes.Strength;
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

        if (hasTrait("Hardy")) {
            health += level;
        }

        getField("Health Maximum").value = health;
    }

// calculate maximum focus (never Enhanced)
    getField("Focus Maximum").value = attributes.Willpower === null
        ? ""
        : 2 + attributes.Willpower + (hasTrait("Composed") ? tier : 0);

// calculate maximum investiture (never Enhanced)
    getField("Investiture Maximum 4").value =
        attributes.Awareness === null && attributes.Presence === null
            ? ""
            : 2 + Math.max(attributes.Awareness, attributes.Presence) +
                (hasTrait("Invested") ? tier : 0);

// calculate movement rate
    var movement = fromTable(effective.Speed, [20, 25, 30, 40, 60, 80]);

    getField("Movement").value = movement === ""
        ? ""
        : (movement + (hasTrait("Surefooted") ? 10 : 0)) + " ft.";

// calculate lifting capacity
    getField("Lifting Capacity").value = fromTable(effective.Strength, [
        "100 lb.", "200 lb.", "500 lb.",
        "1,000 lb.", "5,000 lb.", "10,000 lb."
    ]);

// calculate recovery die
    getField("Recovery Die").value = fromTable(effective.Willpower, [
        "1d4", "1d6", "1d8", "1d10", "1d12", "1d20"
    ]);

// calculate senses range
    getField("Senses Range").value = fromTable(effective.Awareness, [
        "5 ft.", "10 ft.", "20 ft.", "50 ft.", "100 ft.",
        "Unaffected by obscured senses"
    ]);

// calculate unarmed attack damage die
    var unarmedDamage = fromTable(effective.Strength, [
        "1", "1", "1d4", "1d8", "2d6", "2d10"
    ]);

    // Weapons is a free-form box, so only replace the "Unarmed:" line.
    var weaponsField = getField("Weapons");
    var weaponText = weaponsField.valueAsString;
    var weaponLines = weaponText === "" ? [] : weaponText.split(/\r\n|\r|\n/);
    var keptLines = unarmedDamage === "" ? [] : ["Unarmed: " + unarmedDamage];

    for (var w = 0; w < weaponLines.length; w++) {
        if (!/^Unarmed:/.test(weaponLines[w])) {
            keptLines.push(weaponLines[w]);
        }
    }

    var newWeaponText = keptLines.join("\r");

    if (newWeaponText !== weaponText) {
        weaponsField.value = newWeaponText;
    }
})(this);
