async function loadSVG() {
  try {
    const response = await fetch('http://127.0.0.1:8080/api/svg');
    const svgText = await response.text();
    document.getElementById('svgContainer').innerHTML = svgText;
  } catch (error) {
    document.getElementById('svgContainer').textContent = "Error loading SVG.";
  }
}

async function loadQueue() {
  try {
    const response = await fetch('http://127.0.0.1:8080/api/queue_items');
    const data = await response.json();
    const queueList = document.getElementById('queueList');
    queueList.innerHTML = "";

    data.queue_items.forEach((item, index) => {
      const li = document.createElement('li');
      li.textContent = `#${index + 1}: ${item}`;
      queueList.appendChild(li);
    });
  } catch (error) {
    document.getElementById('queueList').textContent = "Error loading queue.";
  }
}

document.getElementById('queueForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const item = document.getElementById('item').value;

  try {
    const response = await fetch('http://127.0.0.1:8080/api/add_queue_item', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "product_id": item })
    });

    const result = await response.json();
    document.getElementById('queueMessage').textContent = result.message || result.detail;
    loadQueue(); // refresh the list
  } catch (err) {
    document.getElementById('queueMessage').textContent = "Failed to add item.";
  }
});

setInterval(() => {
  loadSVG();
  loadQueue();
}, 500);