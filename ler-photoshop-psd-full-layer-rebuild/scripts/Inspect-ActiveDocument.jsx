(function () {
    // Read-only inventory. This does not prove completeness or visual fidelity.
    function quote(s) {
        return '"' + String(s).replace(/["\\\x00-\x1f]/g, function (ch) {
            if (ch === '"') return '\\"';
            if (ch === '\\') return '\\\\';
            var h = ch.charCodeAt(0).toString(16);
            return '\\u' + ('0000' + h).slice(-4);
        }) + '"';
    }
    function json(v) {
        if (v === null || typeof v === 'undefined') return 'null';
        if (typeof v === 'string') return quote(v);
        if (typeof v === 'number') return isFinite(v) ? String(v) : 'null';
        if (typeof v === 'boolean') return v ? 'true' : 'false';
        var values = [], i, k;
        if (v instanceof Array) {
            for (i = 0; i < v.length; i++) values.push(json(v[i]));
            return '[' + values.join(',') + ']';
        }
        for (k in v) if (v.hasOwnProperty(k)) values.push(quote(k) + ':' + json(v[k]));
        return '{' + values.join(',') + '}';
    }
    var report = {
        schemaVersion: 1, photoshopVersion: app.version,
        status: 'no_document', inspectionScope: 'active_document_layer_tree_only',
        visualCompletenessVerified: false, savedReopenVerified: false,
        counts: { groups: 0, text: 0, smartObjects: 0, embeddedSmartObjects: 0,
            linkedSmartObjects: 0, unknownSmartObjects: 0, solidFills: 0, otherLayers: 0 },
        layers: [], layerComps: [], errors: []
    };
    if (!app.documents.length) return json(report);
    var doc = app.activeDocument, s = stringIDToTypeID;
    report.status = 'inspected';
    report.document = { name: doc.name, width: doc.width.as('px'),
        height: doc.height.as('px'), resolution: doc.resolution,
        mode: String(doc.mode), saved: doc.saved, activeLayerId: doc.activeLayer.id };
    function properties(layer) {
        var ref = new ActionReference();
        ref.putIdentifier(s('layer'), layer.id);
        return executeActionGet(ref);
    }
    function walk(parent, parentPath, parentVisible) {
        for (var i = 0; i < parent.layers.length; i++) {
            var layer = parent.layers[i];
            var path = parentPath.concat([layer.name]);
            var entry = { id: layer.id, path: path, visible: layer.visible,
                effectivelyVisible: parentVisible && layer.visible,
                opacity: layer.opacity, blendMode: String(layer.blendMode),
                type: layer.typename };
            report.layers.push(entry);
            if (layer.typename === 'LayerSet') {
                report.counts.groups++;
                walk(layer, path, entry.effectivelyVisible);
                continue;
            }
            entry.kind = String(layer.kind);
            if (layer.kind === LayerKind.TEXT) {
                report.counts.text++;
                try {
                    entry.text = { contents: layer.textItem.contents,
                        font: layer.textItem.font, size: String(layer.textItem.size) };
                } catch (textError) {
                    report.errors.push({ layerId: layer.id, operation: 'text', message: textError.message });
                }
            } else if (layer.kind === LayerKind.SMARTOBJECT) {
                report.counts.smartObjects++;
                entry.smartObject = { linked: null, fileReference: null };
                try {
                    var desc = properties(layer);
                    var so = desc.getObjectValue(s('smartObject'));
                    if (so.hasKey(s('linked'))) {
                        entry.smartObject.linked = so.getBoolean(s('linked'));
                    }
                    if (so.hasKey(s('fileReference'))) {
                        entry.smartObject.fileReference = so.getString(s('fileReference'));
                    }
                    if (desc.hasKey(s('smartObjectMore'))) {
                        var more = desc.getObjectValue(s('smartObjectMore'));
                        if (more.hasKey(s('transform'))) {
                            var tr = more.getList(s('transform')), coords = [];
                            for (var j = 0; j < tr.count; j++) coords.push(tr.getDouble(j));
                            entry.smartObject.transform = coords;
                        }
                    }
                } catch (smartError) {
                    report.errors.push({ layerId: layer.id, operation: 'smartObject', message: smartError.message });
                }
                if (entry.smartObject.linked === true) report.counts.linkedSmartObjects++;
                else if (entry.smartObject.linked === false) report.counts.embeddedSmartObjects++;
                else report.counts.unknownSmartObjects++;
            } else if (layer.kind === LayerKind.SOLIDFILL) {
                report.counts.solidFills++;
            } else {
                report.counts.otherLayers++;
            }
        }
    }
    walk(doc, [], true);
    for (var c = 0; c < doc.layerComps.length; c++) {
        var comp = doc.layerComps[c];
        report.layerComps.push({ name: comp.name, comment: comp.comment });
    }
    report.activeLayerUnchanged = doc.activeLayer.id === report.document.activeLayerId;
    if (report.errors.length) report.status = 'inspected_with_errors';
    return json(report);
}());
