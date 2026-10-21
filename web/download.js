const link = document.querySelector('#download-link');
const status = document.querySelector('#download-status');
// Navigate to the exact published attachment. GitHub responds as a file download.
// Keep this page and its manual button available if the browser blocks it.
setTimeout(() => {
  status.textContent = '已发起下载，请查看浏览器的下载列表。';
  link.click();
}, 700);
