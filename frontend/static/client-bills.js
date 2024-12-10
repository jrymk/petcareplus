const billPStatusSelect = document.getElementById('bill-pstatus');
billPStatusSelect?.addEventListener("change", generateBillIdOptions);

const billIdSelect = document.getElementById('bill-id');
billIdSelect?.addEventListener("change", getBillDetails);


function generateBillIdOptions(){
    fetch('/get_bill_with_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            pStatus: billPStatusSelect.value
        })
    })
    .then(response => response.json())
    .then(data => {
        var billIds = data.bill_ids;
        var selectBillIds = document.getElementById('bill-id');
        for(var i = 0; i < billIds.length; i++) {
            var option = document.createElement("option");
            option.value = billIds[i][0];
            option.text = billIds[i][0];
            selectBillIds.appendChild(option);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function getBillDetails(){
    var billDetailsTable = document.getElementById("bill-details-table")

    fetch('/get_bill_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            billId: billIdSelect.value
        })
    })
    .then(response => response.json())
    .then(data => {
        billDetailsTable.innerHTML = `
            ${data.billHTML}<br>
            ${data.billDetailsHTML}
        `
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}