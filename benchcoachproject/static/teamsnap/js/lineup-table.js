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

function colorPositions(){
    var player_rows = [];
    player_rows.push.apply(player_rows, document.getElementById('table-players-lineup').querySelectorAll('tr'));
    player_rows.push.apply(player_rows, document.getElementById('table-players-bench').querySelectorAll('tr'));
    var label_value_array = []
    player_rows.forEach(function (player_row, index){
        console.dir(player_row)
        if (player_row.querySelector('[name$="label"]')){
            console.dir(player_row.querySelector('select[name$="label"]'))
            console.dir(player_row.querySelector('select[name$="label"]').value)
            label_value_array.push(
                player_row.querySelector('select[name$="label"]').value)
        }
    }
    )
    document.querySelectorAll('[id^="position-status"]').forEach(function(position_status,index){
        if (label_value_array.includes(position_status.innerHTML)){
            if (position_status.classList.contains("text-danger")){
                position_status.classList.remove('text-danger')
            }
            position_status.classList.add('text-success')
        } else {
            if (position_status.classList.contains("text-success")){
                position_status.classList.remove('text-success')
            }
            position_status.classList.add('text-danger')
        }
    })
    console.dir(label_value_array)
}

function refresh_lineup_order (){
    var player_rows = document.getElementById('table-players-lineup').querySelectorAll('tr')
    for (let i = 0; i < player_rows.length; i++) {
        var player_order = player_rows[i].querySelector('[id^="sequence"]')
        var form_element_order = player_rows[i].querySelector('[id$="sequence"]')
        player_order.innerText = parseInt(player_rows[i].dataset.order)
        player_rows[i].dataset.order = i
        form_element_order.value = i
        player_order.innerHTML = i+1
    }
    var player_rows = document.getElementById('table-players-bench').querySelectorAll('tr')
    for (let i = 0; i < player_rows.length; i++) {
        var player_order = player_rows[i].querySelector('[id^="player-order"]')
        var form_element_order = player_rows[i].querySelector('[id$="sequence"]')
        player_rows[i].dataset.order = null
        form_element_order.value = null
        player_order.innerHTML = null
    }
}

var lineup = new Sortable.create(
    document.getElementById('tbody-players-lineup'), {
        animation: 150,
        handle: ".drag-handle",
        ghostClass:"ghost",
        group:{
            put:true,
            pull:true
        },
        onAdd: function (/**Event*/evt) {
            // Add to Lineup
            var itemEl = evt.item;  // dragged HTMLElement
            var player_order = itemEl.querySelector('[id^="sequence-member"]')
            var player_available =itemEl.querySelector('[class^="member-availability-status"]')
            refresh_lineup_order()
            if (player_order.classList.contains('d-none')){
                player_order.classList.remove('d-none')
            }
            // player_available.classList.add('d-none')
        },
        onUpdate: function (/**Event*/evt) {
            console.log('update to lineup')
            var itemEl = evt.item;  // dragged HTMLElement
            refresh_lineup_order()
        },
    });

var bench = new Sortable.create(
    document.getElementById('tbody-players-bench'), {
        animation: 150,
        ghostClass:"ghost",
        sort: false,
        handle: ".drag-handle",
// handle: ".bars-move",
        group:{
            put:true,
            pull:true
        },
        onAdd: function (/**Event*/evt) {
            var itemEl = evt.item;  // dragged HTMLElement
            var player_order = itemEl.querySelector('[id^="sequence-member"]')
            var player_available =itemEl.querySelector('[class^="member-availability-status"]')
            refresh_lineup_order()
            // player_order.classList.add('d-none')
            if (player_order.classList.contains('d-none')){
                player_available.classList.remove('d-none')
            }
        }
    });
//xxx
colorPositions()