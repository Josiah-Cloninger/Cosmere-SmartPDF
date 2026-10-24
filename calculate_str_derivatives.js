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
    var healthMaximumField = doc.getField("Health Maximum");
    healthMaximumField.value = 10 + strength;

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
})(this);