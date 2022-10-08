const plan = document.getElementById('plan');
const main = document.getElementById('main');
const recommendations = ['Restrict', 'Maintain', 'Boost'];

function generatePlan() {
  fetch('/plan')
    .then((response) => response.json())
    .then((data) => {
      const tableBody = document.getElementById('table-body');
      if (data.length) {
        data.forEach((item) => {
          row = document.createElement('tr');
          datecell = document.createElement('td');
          datetime = new Date(item.date);
          datecell.innerHTML = datetime.toLocaleString().slice(0, -3);
          pricecell = document.createElement('td');
          if (item.recommendation == '-') {
            pricecell.className = 'has-background-danger has-text-white';
            pricecell.innerHTML = recommendations[0];
          }
          if (item.recommendation == '0') {
            pricecell.className = 'has-background-warning';
            pricecell.innerHTML = recommendations[1];
          }
          if (item.recommendation == '+') {
            pricecell.className = 'has-background-success has-text-white';
            pricecell.innerHTML = recommendations[2];
          }
          row.appendChild(datecell);
          row.appendChild(pricecell);
          tableBody.appendChild(row);
        });
      }
      plan.style.display = 'block';
      main.style.display = 'none';
    });
}
