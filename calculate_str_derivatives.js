(function (doc) {
    // During validation, event.value contains the new Strength value.
    var strength = Number(event.value);

// calculate physical defense
    var speedField = doc.getField("Speed.Page 1");
    var defenseField = doc.getField("Physical Defense");
    var speed = Number(speedField.valueAsString);

    if (!isFinite(strength) || !isFinite(speed)) {
        return;
    }

    defenseField.value = 10 + strength + speed;


// calculate health
    doc.getField("Health Maximum").value = 10 + strength;

// calculate lifting capacity
    var liftingCapacityField = doc.getField("Lifting Capacity");
    if (strength === 0) {
        liftingCapacityField.value = "100 lb.";;
    } else if (strength === 1 || strength === 2) {
        liftingCapacityField.value = "200 lb.";;
    } else if (strength === 3 || strength === 4) {
        liftingCapacityField.value = "500 lb.";;
    } else if (strength === 5 || strength === 6) {
        liftingCapacityField.value = "1,000 lb.";;
    } else if (strength === 7 || strength === 8) {
        liftingCapacityField.value = "5,000 lb.";;
    } else if (strength >= 9) {
        liftingCapacityField.value = "10,000 lb.";;
    }

    // calculate unarmed attack damage die
    var weaponsField = doc.getField("Weapons");
    var unarmedDamage;
    if (strength === 0 || strength === 1 || strength === 2) {
        unarmedDamage = "1";
    } else if (strength === 3 || strength === 4) {
        unarmedDamage = "1d4";;
    } else if (strength === 5 || strength === 6) {
        unarmedDamage = "1d8";;
    } else if (strength === 7 || strength === 8) {
        unarmedDamage = "2d6";;
    } else if (strength >= 9) {
        unarmedDamage = "2d10";;
    }

    // calculate strength-based skill modifiers 
    //      (Athletics, Heavy Weaponry, Tension surge)
    /*
    var skills = [
        ["Athletics", "Athletics"],
        ["Heavy Weapons", "Heavy Weaponry"],
    ];

    for (var i = 0; i < skills.length; i++) {
        var outputName = skills[i][0];
        var statName = "Strength.Page 1";
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
    }*/
})(this);