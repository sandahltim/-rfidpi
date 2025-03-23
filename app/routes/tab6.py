{% extends "base.html" %}
{% block content %}

<h1 style="color: #2c3e50; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">Resale Inventory</h1>

<form method="GET" class="mb-3 row g-2">
  <div class="col-12 col-md-2">
    <input type="text" class="form-control" name="common_name" placeholder="Filter Common Name" value="{{ filter_common_name }}" />
  </div>
  <div class="col-12 col-md-2">
    <input type="text" class="form-control" name="tag_id" placeholder="Filter Tag ID" value="{{ filter_tag_id }}" />
  </div>
  <div class="col-12 col-md-2">
    <input type="text" class="form-control" name="last_contract_num" placeholder="Filter Last Contract" value="{{ filter_last_contract }}" />
  </div>
  <div class="col-12 col-md-2">
    <input type="text" class="form-control" name="rental_class_num" placeholder="Filter Rental Class (54321)" value="{{ filter_rental_class_num }}" />
  </div>
  <div class="col-12 col-md-2">
    <button type="submit" class="btn btn-primary" style="background: #e74c3c; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: all 0.3s;">Apply Filters</button>
  </div>
</form>

<div class="table-container">
  <table class="table table-striped table-bordered" id="parentTable" style="border: 3px solid #2c3e50;">
    <thead style="background: #34495e; color: #ecf0f1;">
      <tr>
        <th style="width: 50px;"></th>
        <th class="sortable" data-col-name="category">Category</th>
        <th class="sortable" data-col-name="total_amount">Total Amount</th>
        <th class="sortable" data-col-name="on_contract">Items on Contract</th>
        <th style="width: 100px;">Print Aggregate</th>
      </tr>
    </thead>
    <tbody>
      {% for parent in parent_data %}
      {% set cat_key = parent.category|lower|replace(' ', '_')|replace(',', '')|replace('.', '')|replace('(', '')|replace(')', '') %}
      <tr class="table-active" style="background: linear-gradient(to right, #ecf0f1, #dfe6e9);">
        <td><span class="expand-toggle" data-bs-toggle="collapse" data-bs-target="#middle-{{ cat_key }}">+</span></td>
        <td>{{ parent.category }}</td>
        <td>{{ parent.total_amount }}</td>
        <td>{{ parent.on_contract }}</td>
        <td><button class="btn btn-outline-dark btn-sm print-aggregate-btn" data-category="{{ parent.category }}" style="border: 2px solid #2c3e50; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: all 0.3s;">Print</button></td>
      </tr>
      <tr>
        <td colspan="5" class="p-0">
          <div id="middle-{{ cat_key }}" class="collapse" data-category="{{ parent.category }}">
            <div class="child-table-container">
              <table class="table table-striped table-bordered middle-table" id="middleTable-{{ cat_key }}" style="border: 2px solid #34495e;">
                <thead style="background: #3498db; color: #fff;">
                  <tr>
                    <th style="width: 50px;"></th>
                    <th class="sortable" data-col-name="common_name">Common Name</th>
                    <th class="sortable" data-col-name="total">Total</th>
                    <th style="width: 100px;">Print Items</th>
                  </tr>
                </thead>
                <tbody>
                  {% for middle in middle_map[parent.category] %}
                  {% set middle_key = cat_key ~ '_' ~ middle.common_name|lower|replace(' ', '_')|replace(',', '')|replace('.', '')|replace('(', '')|replace(')', '') %}
                  <tr class="child-row table-success">
                    <td><span class="expand-toggle" data-bs-toggle="collapse" data-bs-target="#child-{{ middle_key }}">+</span></td>
                    <td>{{ middle.common_name }}</td>
                    <td>{{ middle.total }}</td>
                    <td><button class="btn btn-outline-dark btn-sm print-items-btn" data-category="{{ parent.category }}" data-common-name="{{ middle.common_name }}" style="border: 2px solid #2c3e50; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: all 0.3s;">Print</button></td>
                  </tr>
                  <tr>
                    <td colspan="4" class="p-0">
                      <div id="child-{{ middle_key }}" class="collapse" data-category="{{ parent.category }}" data-common-name="{{ middle.common_name }}">
                        <div class="grandchild-table-container">
                          <table class="table mb-0 grandchild-table" id="grandchildTable-{{ middle_key }}" style="border: 2px solid #2c3e50;">
                            <thead style="background: #2c3e50; color: #ecf0f1;">
                              <tr>
                                <th class="sortable" data-col-name="tag_id">Tag ID</th>
                                <th class="sortable" data-col-name="common_name">Common Name</th>
                                <th class="sortable" data-col-name="status">Status</th>
                                <th class="sortable" data-col-name="bin_location">Bin Location</th>
                                <th class="sortable" data-col-name="quality">Quality</th>
                                <th class="sortable" data-col-name="date_last_scanned">Date Last Scanned</th>
                                <th class="sortable" data-col-name="last_scanned_by">Last Scanned By</th>
                              </tr>
                            </thead>
                            <tbody id="grandchildTbody-{{ middle_key }}"></tbody>
                          </table>
                        </div>
                      </div>
                    </td>
                  </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          </div>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<script>
document.addEventListener("DOMContentLoaded", () => {
    console.log("Tab6 DOM Content Loaded");

    function sortTable(tableEl, colName) {
        let tbody = tableEl.querySelector("tbody");
        if (!tbody) return;

        let asc = tableEl.getAttribute("data-sort-col") === colName 
                  ? tableEl.getAttribute("data-sort-dir") !== "asc" 
                  : true;
        tableEl.setAttribute("data-sort-col", colName);
        tableEl.setAttribute("data-sort-dir", asc ? "asc" : "desc");

        let headers = Array.from(tableEl.querySelectorAll("th"));
        let colIndex = headers.findIndex(th => th.getAttribute("data-col-name") === colName);

        if (tableEl.id === "parentTable") {
            let rows = Array.from(tbody.children);
            let pairs = [];
            for (let i = 0; i < rows.length; i += 2) {
                let parentRow = rows[i];
                let childRow = rows[i + 1] || null;
                if (parentRow && parentRow.classList.contains("table-active")) {
                    pairs.push({ parent: parentRow, child: childRow });
                }
            }
            pairs.sort((a, b) => {
                let cellA = a.parent.cells[colIndex]?.innerText.trim() || "";
                let cellB = b.parent.cells[colIndex]?.innerText.trim() || "";
                let numA = parseFloat(cellA.replace(/[^0-9.\-]/g, ""));
                let numB = parseFloat(cellB.replace(/[^0-9.\-]/g, ""));
                if (!isNaN(numA) && !isNaN(numB)) {
                    return asc ? numA - numB : numB - numA;
                }
                return asc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            });
            tbody.innerHTML = "";
            pairs.forEach(pair => {
                tbody.appendChild(pair.parent);
                if (pair.child) tbody.appendChild(pair.child);
            });
        } else if (tableEl.classList.contains("middle-table")) {
            let rows = Array.from(tbody.children);
            let pairs = [];
            for (let i = 0; i < rows.length; i += 2) {
                let childRow = rows[i];
                let grandRow = rows[i + 1] || null;
                if (childRow && childRow.classList.contains("child-row")) {
                    pairs.push({ child: childRow, grand: grandRow });
                }
            }
            pairs.sort((a, b) => {
                let cellA = a.child.cells[colIndex]?.innerText.trim() || "";
                let cellB = b.child.cells[colIndex]?.innerText.trim() || "";
                let numA = parseFloat(cellA.replace(/[^0-9.\-]/g, ""));
                let numB = parseFloat(cellB.replace(/[^0-9.\-]/g, ""));
                if (!isNaN(numA) && !isNaN(numB)) {
                    return asc ? numA - numB : numB - numA;
                }
                return asc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            });
            tbody.innerHTML = "";
            pairs.forEach(pair => {
                tbody.appendChild(pair.child);
                if (pair.grand) tbody.appendChild(pair.grand);
            });
        } else {
            let rows = Array.from(tbody.querySelectorAll("tr"));
            rows.sort((a, b) => {
                let cellA = a.cells[colIndex]?.innerText.trim() || "";
                let cellB = b.cells[colIndex]?.innerText.trim() || "";
                let numA = parseFloat(cellA.replace(/[^0-9.\-]/g, ""));
                let numB = parseFloat(cellB.replace(/[^0-9.\-]/g, ""));
                if (!isNaN(numA) && !isNaN(numB)) {
                    return asc ? numA - numB : numB - numA;
                }
                return asc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            });
            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));
        }
    }

    document.querySelectorAll(".sortable").forEach(th => {
        th.addEventListener("click", () => {
            const table = th.closest("table");
            const colName = th.getAttribute("data-col-name");
            sortTable(table, colName);
        });
    });
});
</script>

<style>
  .table-danger { background: #ffcccc; }
  .table-warning { background: #ffff99; }
  .table-success { background: #ccffcc; }
  body, html {
    height: 100%;
    overflow-y: auto;
    margin: 0;
    padding: 0;
  }
  .table-container {
    width: 100%;
    overflow-y: visible;
    padding-bottom: 100px;
  }
  .table-container table {
    width: 100%;
    table-layout: auto;
  }
  .child-table-container {
    width: 100%;
    overflow-y: visible;
  }
  .child-table-container table {
    width: 100%;
    table-layout: auto;
  }
  .grandchild-table-container {
    width: 100%;
    overflow-y: visible;
  }
  .grandchild-table-container table {
    width: 100%;
    table-layout: auto;
  }
  .collapse {
    width: 100%;
  }
  @media (max-width: 768px) {
    .pagination .page-link { padding: 0.25rem 0.5rem; font-size: 0.9rem; }
  }
</style>

{% endblock %}