document.querySelector('form').addEventListener('submit', (e) => {
    const orderId = document.getElementById('orderid').value;
    if (!orderId || orderId <= 0) {
      e.preventDefault();
      alert('Please enter a valid Order ID.');
    }
  });
  