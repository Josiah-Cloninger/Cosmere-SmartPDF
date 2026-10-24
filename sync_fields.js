(function (doc, source) {
    var pageSuffix = /\.Page \d+$/;
    var baseName = source.name.replace(pageSuffix, "");
    var newValue = source.valueAsString;

    if (!pageSuffix.test(source.name)) {
        return;
    }

    for (var i = 0; i < doc.numFields; i++) {
        var name = doc.getNthFieldName(i);

        if (
            name !== source.name &&
            pageSuffix.test(name) &&
            name.replace(pageSuffix, "") === baseName
        ) {
            var other = doc.getField(name);

            if (other !== null && other.valueAsString !== newValue) {
                other.value = newValue;
            }
        }
    }
})(this, event.target);