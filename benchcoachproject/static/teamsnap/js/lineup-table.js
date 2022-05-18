function positionSelectChanged(elem) {
    let row = elem.parentElement.parentElement
    let original_table = elem.parentElement.parentElement.parentElement
    let lineup_table = document.getElementById('lineup')
    let bench_table = document.getElementById('bench')
    let dhd_table = document.getElementById('dhd')
    let player_order = row.querySelector('[id^="player-order"]')
    let player_available = row.querySelector('[id^="player-availability"]')

    console.dir(original_table == bench_table)
    if (elem.value == "P" && original_table == bench_table ) {
        dhd_table.appendChild(row)
        player_order.classList.remove('d-none')
        // player_available.classList.add('d-none')
        refresh_lineup_order()
    }
    else if (elem.value && original_table == dhd_table ) {
        dhd_table.appendChild(row)
        player_order.classList.remove('d-none')
        // player_available.classList.add('d-none')
        refresh_lineup_order()
    }
    else if (elem.value) {
        lineup_table.appendChild(row)
        player_order.classList.remove('d-none')
        // player_available.classList.add('d-none')
        refresh_lineup_order()
    }
    else {
        bench_table.prepend(row)
        // player_order.classList.add('d-none')
        player_available.classList.remove('d-none')
    }
}

function colorPositions() {
    for (bcLineup of document.getElementsByClassName("benchcoach-lineup")) {
        var player_rows = bcLineup.querySelectorAll('tr');
        // player_rows.push.apply(player_rows, document.getElementsByClassName('benchcoach-lineup').querySelectorAll('tr'));
        // player_rows.push.apply(player_rows, document.getElementsByClassName('benchcoach-bench').querySelectorAll('tr'));
        var label_value_array = []
        player_rows.forEach(function (player_row, index) {
                if (player_row.querySelector('[name$="label"]')) {
                    label_value_array.push(
                        player_row.querySelector('select[name$="label"]').value)
                }
            }
        )
        bcLineup.querySelectorAll('[id^="position-status"]').forEach(function (position_status, index) {
            if (label_value_array.includes(position_status.innerHTML)) {
                if (position_status.classList.contains("text-danger")) {
                    position_status.classList.remove('text-danger')
                }
                position_status.classList.add('text-success')
            } else {
                if (position_status.classList.contains("text-success")) {
                    position_status.classList.remove('text-success')
                }
                position_status.classList.add('text-danger')
            }
            // console.dir(position_status)
        })
        // console.dir(label_value_array)
    }
}

function refresh_lineup_order (itemEl){
    let bcLineup = itemEl.closest(".benchcoach-lineup")
    var player_rows = []
    for (tbody of bcLineup.querySelectorAll("[class*='tbody-benchcoach-starting']")){
        for (row of tbody.rows){
            player_rows.push(row)
        }
    }

    for (let i = 0; i < player_rows.length; i++) {
        var player_order = player_rows[i].querySelector('[id^="sequence"]')
        var form_element_order = player_rows[i].querySelector('[id$="sequence"]')
        player_order.innerText = parseInt(player_rows[i].dataset.order)
        player_rows[i].dataset.order = i
        form_element_order.value = i
        player_order.innerHTML = i+1
    }
    var player_rows = bcLineup.getElementsByClassName("tbody-benchcoach-bench")[0].rows
    for (let i = 0; i < player_rows.length; i++) {
        var player_order = player_rows[i].querySelector('[id^="sequence"]')
        var form_element_order = player_rows[i].querySelector('[id$="sequence"]')
        player_rows[i].dataset.order = null
        form_element_order.value = null
        player_order.innerHTML = null
    }
}

function sendToClipboard(itemEl){
    let bcLineup = itemEl.closest(".benchcoach-lineup")
    player_rows = bcLineup.querySelectorAll("[data-position=P]")
    lineup_export = []
    if (player_rows.length > 0){
        lineup_export.push(player_rows[0].dataset.playerName)
        lineup_export.push("","")
    } else {
        lineup_export.push("","","")
    }

    lineup_export.push("")
    for (position of [
        'C',
        '1B',
        '2B',
        '3B',
        'SS',
        'LF',
        'CF',
        'RF',
        'DH',
    ]
        ) {
        var player_rows = bcLineup.querySelectorAll(`[data-position=${CSS.escape(position)}]`)
        if (player_rows.length > 0){
            lineup_export.push(player_rows[0].dataset.playerName)
        } else {
            lineup_export.push('')
        }
    }
    for (position of [
        'EH',
    ]
        ) {
        var player_rows = bcLineup.querySelectorAll(`[data-position=${CSS.escape(position)}]`)
        for (var i = 0; i < 2; i++) {
            if (i < player_rows.length){
                lineup_export.push(player_rows[i].dataset.playerName)
            } else {
                lineup_export.push("")
            }
        }
    }

    for (position of [
        'DR',
    ]
        ) {
        let player_rows = bcLineup.querySelectorAll(`[data-position=${CSS.escape(position)}]`)
        if (player_rows.length > 0){
            lineup_export.push(player_rows[0].dataset.playerName)
        } else {
            lineup_export.push('')
        }
    }

    lineup_export.push("")
    lineup_export.push("","")
    lineup_export.push("")

    for (var i = 0; i < 11; i++) {
        let player_rows = bcLineup.querySelectorAll(`[data-order=${CSS.escape(i)}]`)
        if (player_rows.length > 0){
            lineup_export.push(player_rows[0].dataset.playerName)
        } else {
            lineup_export.push("")
        }
    }

    console.dir(lineup_export)
    var textArea = document.createElement("textarea");
    textArea.value = lineup_export.join("\n");

    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        var successful = document.execCommand('copy');
        var msg = successful ? 'successful' : 'unsuccessful';
        console.log('Copying text command was ' + msg);
    } catch (err) {
        console.error('Oops, unable to copy', err);
    }

    document.body.removeChild(textArea);

}

benchcoach_lineups = document.getElementsByClassName("benchcoach-lineup")
for (bcLineup of document.getElementsByClassName("benchcoach-lineup")) {
    var startinglineup = new Sortable.create(
        bcLineup.getElementsByClassName("tbody-benchcoach-startinglineup")[0], {
            animation: 150,
            handle: ".drag-handle",
            ghostClass:"ghost",
            group:{
                name:bcLineup.id,
                put:[bcLineup.id],
                pull:[bcLineup.id]
            },
            onAdd: function (/**Event*/evt) {
                // Add to Lineup
                var itemEl = evt.item;  // dragged HTMLElement
                var player_order = itemEl.querySelector('[id^="sequence-member"]')
                var player_available =itemEl.querySelector('[class^="member-availability-status"]')
                refresh_lineup_order(itemEl)
                if (player_order.classList.contains('d-none')){
                    player_order.classList.remove('d-none')
                }
                // player_available.classList.add('d-none')
            },
            onUpdate: function (/**Event*/evt) {
                console.log('update to lineup')
                var itemEl = evt.item;  // dragged HTMLElement
                refresh_lineup_order(itemEl)
            },
        });

    var bench = new Sortable.create(
        bcLineup.getElementsByClassName("tbody-benchcoach-bench")[0], {
            animation: 150,
            ghostClass:"ghost",
            sort: false,
            handle: ".drag-handle",
// handle: ".bars-move",
            group:{
                name:bcLineup.id,
                put:[bcLineup.id],
                pull:[bcLineup.id]
            },
            onAdd: function (/**Event*/evt) {
                var itemEl = evt.item;  // dragged HTMLElement
                var player_order = itemEl.querySelector('[id^="sequence-member"]')
                var player_available =itemEl.querySelector('[class^="member-availability-status"]')
                refresh_lineup_order(itemEl)
                // player_order.classList.add('d-none')
                if (player_order.classList.contains('d-none')){
                    player_available.classList.remove('d-none')
                }
            }
        });

    var positionalonlylineup = new Sortable.create(
        bcLineup.getElementsByClassName("tbody-benchcoach-startingpositionalonly")[0], {
            handle: ".drag-handle",
            group:{
                name:bcLineup.id,
                put:[bcLineup.id],
                pull:[bcLineup.id]
            },
            onAdd: function (/**Event*/evt) {
                var itemEl = evt.item;  // dragged HTMLElement
                var player_order = itemEl.querySelector('[id^="sequence-member"]')
                var position_only = itemEl.querySelector('[id$="position_only"]')
                position_only.value = true
                var player_available =itemEl.querySelector('[class^="member-availability-status"]')
                refresh_lineup_order(itemEl)
                // player_order.classList.add('d-none')
                if (player_order.classList.contains('d-none')){
                    player_available.classList.remove('d-none')
                }
            },
            onRemove: function (/**Event*/evt) {
                var itemEl = evt.item;  // dragged HTMLElement
                var player_order = itemEl.querySelector('[id^="sequence-member"]')
                var player_available =itemEl.querySelector('[class^="member-availability-status"]')
                var position_only = itemEl.querySelector('[id$="position_only"]')
                position_only.value = false

                if (player_order.classList.contains('d-none')){
                    player_available.classList.remove('d-none')
                }
            },
            onUpdate: function (/**Event*/evt) {
                var itemEl = evt.item;  // dragged HTMLElement
                refresh_lineup_order(itemEl)
            },
        }

    )
}

function copyEmailTable(itemEl, subject, recipients){
    // Create container for the HTML
    // [1]
    let bcLineup = itemEl.closest(".benchcoach-lineup")
    var container = document.createElement('div')
    var tbl = document.createElement('table')

    let thead = tbl.createTHead()
    let thead_row = thead.insertRow()
    let thead_row_cell = thead_row.insertCell()
    thead_row_cell.appendChild(document.createElement("h3").appendChild(document.createTextNode("STARTING LINEUP")))
    thead_row_cell.colSpan=3;
    thead_row_cell.classList.add('title-cell')
    var tbody = tbl.createTBody()
    for (row of bcLineup.querySelector(".table-benchcoach-startinglineup").rows) {
        let tr = tbody.insertRow()
        cell = tr.insertCell()
        cell.classList.add('sequence-cell')
        cell.appendChild(document.createTextNode((parseInt(row.dataset.order) + 1)))
        cell = tr.insertCell()
        cell.appendChild(document.createTextNode(row.dataset.playerName))
        cell.classList.add('name-cell')
        tr.insertCell().appendChild(document.createTextNode(row.dataset.position))
    }

    if (bcLineup.querySelector('.table-benchcoach-startingpositionalonly').rows.length > 0) {
        var tr = tbody.insertRow()
        cell = tr.insertCell()
        cell.colSpan=3
        cell.appendChild(document.createTextNode("STARTING (POS. ONLY)"))
        cell.classList.add('title-cell')

        for (row of bcLineup.querySelector('.table-benchcoach-startingpositionalonly').rows) {
            var tr = tbody.insertRow()
            cell = tr.insertCell()
            cell.classList.add('sequence-cell')
            cell.appendChild(document.createTextNode(""))
            cell=tr.insertCell()
            cell.appendChild(document.createTextNode(row.dataset.playerName))
            cell.classList.add('name-cell')
            tr.insertCell().appendChild(document.createTextNode(row.dataset.position))
        }
    }

    if (bcLineup.querySelector('.table-benchcoach-bench').rows.length > 0) {
        var tr = tbody.insertRow()
        cell = tr.insertCell()
        cell.colSpan=3
        cell.appendChild(document.createTextNode("SUBS"))
        cell.classList.add('title-cell')

        for (row of bcLineup.querySelector('.table-benchcoach-bench').rows) {
            var tr = tbody.insertRow()
            cell = tr.insertCell()
            cell.classList.add('sequence-cell')
            availability_status = {
                None: "UNK",
                "0": "NO",
                "2": "MAY",
                "1":"YES"
            }[row.dataset.availabilityStatuscode]
            cell.appendChild(document.createTextNode(availability_status))
            cell=tr.insertCell()
            cell.appendChild(document.createTextNode(row.dataset.playerName))
            cell.classList.add('name-cell')
            tr.insertCell().appendChild(document.createTextNode(""))
        }
    }

    if (bcLineup.querySelector('.table-benchcoach-out').rows.length > 0) {
        var tr = tbody.insertRow()
        cell = tr.insertCell()
        cell.colSpan=3
        cell.appendChild(document.createTextNode("OUT"))
        cell.classList.add('title-cell')

        for (row of bcLineup.querySelector('.table-benchcoach-out').rows) {
            var tr = tbody.insertRow()
            cell = tr.insertCell()
            cell.classList.add('sequence-cell')
            availability_status = {
                "None": "UNK",
                "0": "NO",
                "1": "MAY",
                "2":"YES"
            }[row.dataset.availabilityStatuscode]
            cell.appendChild(document.createTextNode(availability_status))
            tr.insertCell().appendChild(document.createTextNode(row.dataset.playerName))
            tr.insertCell().appendChild(document.createTextNode(""))
        }
    }

    container.appendChild(tbl)
    for (cell of container.getElementsByClassName('title-cell')){
        cell.setAttribute (
            "style",
            "font-weight:bold;background-color:#323669;color:#fff;padding:2px 5px;"
        )}

    for (cell of container.getElementsByClassName('sequence-cell')){
        cell.setAttribute (
            "style",
            "font-weight:bold;padding:2px 5px;"
        )}

    for (cell of container.getElementsByClassName('name-cell')){
        cell.setAttribute (
            "style",
            "width:200px;"
        )}

    // Detect all style sheets of the page
    var activeSheets = Array.prototype.slice.call(document.styleSheets)
        .filter(function (sheet) {
            return !sheet.disabled
        })

    // Mount the container to the DOM to make `contentWindow` available
    // [3]
    document.body.appendChild(container)

    // Copy to clipboard
    // [4]
    window.getSelection().removeAllRanges()

    var range = document.createRange()
    range.selectNode(container)
    window.getSelection().addRange(range)

    // [5.1]
    document.execCommand('copy')

    // [5.2]
    for (var i = 0; i < activeSheets.length; i++) activeSheets[i].disabled = true

    // [5.3]
    // document.execCommand('copy')

    // [5.4]
    for (var i = 0; i < activeSheets.length; i++) activeSheets[i].disabled = false

    // Remove the container
    // [6]
    document.body.removeChild(container)
    subject_encoded = encodeURIComponent(subject)
    window.open("readdle-spark://compose?recipient=manager@chihounds.com&subject="+subject+"&bcc="+recipients)
}

function copyHtmlTable(itemEl){
    // Create container for the HTML
    // [1]
    var container = document.createElement('div')
    let bcLineup = itemEl.closest(".benchcoach-lineup")
    // container.appendChild(bcLineup.cloneNode(true))
    // console.dir(container)
    container.tab
    container.appendChild(bcLineup.querySelector('.table-benchcoach-startinglineup').cloneNode(false))
    header_row = container.querySelector(".table-benchcoach-startinglineup").insertRow(0);
    header_row_cell = header_row.insertCell(0);
    header_row_cell.colSpan=5;
    header_row_cell.innerHTML = "STARTING LINEUP";

    for (r of bcLineup.querySelector('.table-benchcoach-startinglineup').rows){
        new_row = r.cloneNode(true)
        container.querySelector(".table-benchcoach-startinglineup").appendChild(new_row)
        for (s of new_row.querySelectorAll("span")){
            s.classList.remove('d-none')
        }
    }

    if (bcLineup.querySelector('.table-benchcoach-startingpositionalonly').rows.length > 0){
        header_row = container.querySelector(".table-benchcoach-startingpositionalonly").insertRow()
        header_row_cell = header_row.insertCell(0)
        header_row_cell.colSpan=5
        header_row_cell.innerHTML = "POSITIONAL ONLY"

        for (r of bcLineup.querySelector('.table-benchcoach-startingpositionalonly').rows){
            for (s of r.querySelectorAll("span")){
                console.dir(r)
                s.classList.remove('d-none')
            }
            new_row = container.querySelector(".table-benchcoach-startinglineup").insertRow()
            new_row.outerHTML = r.outerHTML
        }
    }

    header_row = container.querySelector(".table-benchcoach-startinglineup").insertRow()
    header_row_cell = header_row.insertCell(0)
    header_row_cell.colSpan=5
    header_row_cell.innerHTML = "SUBS"

    for (row of bcLineup.querySelector('.table-benchcoach-bench').rows){
        for (s of row.querySelectorAll("span")){
            s.classList.remove('d-none')
        }
        new_row = container.querySelector(".table-benchcoach-startinglineup").insertRow()
        new_row.outerHTML = row.outerHTML
    }

    header_row = container.querySelector(".table-benchcoach-startinglineup").insertRow()
    header_row_cell = header_row.insertCell(0)
    header_row_cell.colSpan=5
    header_row_cell.innerHTML = "OUT"

    for (r of bcLineup.querySelector('.table-benchcoach-out').rows){
        new_row = container.querySelector(".table-benchcoach-startinglineup").insertRow()
        new_row.outerHTML = r.outerHTML
    }

    console.dir(container)
    // container.hidden = true
    for (f of container.querySelectorAll(".lineup-label-form")){
        // f.firstElementChild.hidden = true
        f.innerHTML = f.firstElementChild.options[f.firstElementChild.selectedIndex].value
    }
    for (f of container.querySelectorAll(".position-status")){
        f.remove()
    }
    // container.querySelectorAll(".lineup-label-form").firstElementChild.hidden = true

    // Hide element
    // [2]
    container.style.position = 'fixed'
    container.style.pointerEvents = 'none'
    container.style.opacity = 0

    // Detect all style sheets of the page
    var activeSheets = Array.prototype.slice.call(document.styleSheets)
        .filter(function (sheet) {
            return !sheet.disabled
        })

    // Mount the container to the DOM to make `contentWindow` available
    // [3]
    document.body.appendChild(container)

    // Copy to clipboard
    // [4]
    window.getSelection().removeAllRanges()

    var range = document.createRange()
    range.selectNode(container)
    window.getSelection().addRange(range)

    // [5.1]
    document.execCommand('copy')

    // [5.2]
    for (var i = 0; i < activeSheets.length; i++) activeSheets[i].disabled = true

    // [5.3]
    // document.execCommand('copy')

    // [5.4]
    for (var i = 0; i < activeSheets.length; i++) activeSheets[i].disabled = false

    // Remove the container
    // [6]
    document.body.removeChild(container)
}

//xxx
colorPositions()